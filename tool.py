import pyautogui
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import json
import time
import threading
import traceback
from pynput.mouse import Listener, Button
from pynput.keyboard import Listener as KeyboardListener, Key, KeyCode
import numpy as np

# Tắt tính năng failsafe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.005

# Biến toàn cục
actions = []
is_recording = False
is_replaying = False
start_time = 0
last_position = None
is_dragging = False
last_recorded_time = 0
stop_replay_event = threading.Event()


def interpolate_positions(start_pos, end_pos, steps):
    """Tạo các điểm trung gian giữa hai vị trí."""
    if not start_pos or not end_pos:
        return []
    x = np.linspace(start_pos[0], end_pos[0], steps)
    y = np.linspace(start_pos[1], end_pos[1], steps)
    return list(zip(x, y))


def validate_actions(actions):
    """Kiểm tra tính hợp lệ của danh sách hành động."""
    try:
        if not isinstance(actions, list):
            return False
        for action in actions:
            required_keys = ["time", "type"]
            if not all(key in action for key in required_keys):
                return False
            if not isinstance(action["time"], (int, float)):
                return False
            if action["type"] not in ["click", "drag", "scroll", "release"]:
                return False
            if action["type"] != "release" and not all(key in action for key in ["x", "y"]):
                return False
            if action["type"] in ["click", "drag", "release"] and "button" not in action:
                return False
            if action["type"] == "scroll" and "dx" not in action and "dy" not in action:
                return False
        return True
    except Exception:
        return False


def on_move(x, y):
    """Xử lý sự kiện di chuyển chuột."""
    global actions, is_recording, start_time, last_position, is_dragging
    if is_recording and is_dragging:
        current_time = time.time() - start_time
        action = {
            "time": current_time,
            "type": "drag",
            "x": x,
            "y": y,
            "button": "left"
        }
        actions.append(action)
        print(f"Đã ghi lại hành động kéo: {action}")
        last_position = (x, y)


def on_click(x, y, button, pressed):
    """Xử lý sự kiện click chuột."""
    global actions, is_recording, start_time, is_dragging
    if is_recording:
        current_time = time.time() - start_time
        if pressed:
            is_dragging = True
            action = {
                "time": current_time,
                "type": "click",
                "x": x,
                "y": y,
                "button": str(button)
            }
        else:
            is_dragging = False
            action = {
                "time": current_time,
                "type": "release",
                "button": str(button)
            }
        actions.append(action)
        print(f"Đã ghi lại hành động click: {action}")


def on_scroll(x, y, dx, dy):
    """Xử lý sự kiện lăn chuột."""
    global actions, is_recording, start_time
    if is_recording:
        current_time = time.time() - start_time
        action = {
            "time": current_time,
            "type": "scroll",
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy
        }
        actions.append(action)
        print(f"Đã ghi lại hành động lăn: {action}")


def record_actions():
    """Bắt đầu ghi hành động."""
    global is_recording, actions, start_time, last_position, is_dragging
    try:
        is_recording = True
        actions = []
        start_time = time.time()
        last_position = None
        is_dragging = False
        print("Bắt đầu ghi hành động...")
        messagebox.showinfo("Ghi Hành Động", "Bắt đầu ghi sau khi bấm OK.")

        mouse_listener = Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll
        )
        mouse_listener.start()

        def stop_listener():
            mouse_listener.stop()
            print("Listener đã dừng.")

        root.protocol("WM_DELETE_WINDOW", stop_listener)

    except Exception as e:
        print(f"Lỗi khi bắt đầu ghi: {e}")
        print(traceback.format_exc())


def stop_recording():
    """Dừng ghi hành động."""
    global is_recording
    try:
        is_recording = False
        print("Dừng ghi hành động.")
        messagebox.showinfo("Ghi Hành Động", "Đã dừng ghi.")
    except Exception as e:
        print(f"Lỗi khi dừng ghi: {e}")
        print(traceback.format_exc())


def save_actions():
    """Lưu hành động vào tệp JSON."""
    global actions
    try:
        print(f"Actions hiện tại: {actions}")
        if not actions:
            messagebox.showwarning("Lưu", "Không có hành động nào để lưu.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Tập tin JSON", "*.json")]
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(actions, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Lưu", f"Đã lưu hành động thành công vào {filepath}!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu hành động: {str(e)}")


def load_actions():
    """Tải hành động từ tệp JSON."""
    global actions
    try:
        filepath = filedialog.askopenfilename(filetypes=[("Tập tin JSON", "*.json")])
        if not filepath:
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_actions = json.load(f)

        if not validate_actions(loaded_actions):
            messagebox.showerror("Lỗi", "Định dạng dữ liệu trong tập tin không hợp lệ.")
            return

        actions = loaded_actions
        messagebox.showinfo("Tải", f"Đã tải hành động thành công từ {filepath}!")
    except json.JSONDecodeError:
        messagebox.showerror("Lỗi", "Định dạng tập tin JSON không hợp lệ.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải hành động: {str(e)}")


def replay_actions(root):
    """Phát lại các hành động đã ghi."""
    global actions, is_replaying, stop_replay_event
    try:
        if not actions:
            messagebox.showwarning("Phát Lại", "Không có hành động nào để phát lại.")
            return

        result = tk.IntVar()

        def ask_repeat():
            repeat = simpledialog.askinteger("Phát Lại", "Nhập số lần phát lại:", minvalue=1)
            if repeat is not None:
                result.set(repeat)
            else:
                result.set(0)

        root.after(0, ask_repeat)
        root.wait_variable(result)

        repeat = result.get()
        if repeat <= 0:
            return

        stop_replay_event.clear()

        def replay():
            global is_replaying
            is_replaying = True
            messagebox.showinfo("Phát Lại", "Bắt đầu phát lại.")

            for _ in range(repeat):
                if stop_replay_event.is_set():
                    break

                start_time = time.time()
                mouse_down = False
                last_pos = None

                for action in actions:
                    if stop_replay_event.is_set():
                        break

                    current_time = time.time() - start_time
                    wait_time = action["time"] - current_time
                    if wait_time > 0:
                        time.sleep(max(0, min(wait_time, 0.05)))

                    try:
                        if action["type"] == "click":
                            button = action["button"].replace("Button.", "").lower()
                            pyautogui.mouseDown(action["x"], action["y"], button=button)
                            mouse_down = True
                            last_pos = (action["x"], action["y"])

                        elif action["type"] == "release":
                            button = action["button"].replace("Button.", "").lower()
                            pyautogui.mouseUp(button=button)
                            mouse_down = False

                        elif action["type"] == "drag":
                            current_pos = (action["x"], action["y"])
                            if last_pos:
                                distance = ((current_pos[0] - last_pos[0]) ** 2 +
                                            (current_pos[1] - last_pos[1]) ** 2) ** 0.5
                                steps = max(2, min(20, int(distance / 10)))
                                positions = interpolate_positions(last_pos, current_pos, steps)

                                for pos in positions:
                                    if stop_replay_event.is_set():
                                        break
                                    pyautogui.dragTo(pos[0], pos[1], duration=0.01)
                            else:
                                pyautogui.dragTo(action["x"], action["y"], duration=0.01)
                            last_pos = current_pos

                        elif action["type"] == "scroll":
                            # Scroll theo chiều dọc
                            pyautogui.scroll(int(action["dy"] * 120))
                            # Scroll theo chiều ngang nếu có
                            if action.get("dx", 0) != 0:
                                pyautogui.hscroll(int(action["dx"] * 120))

                    except KeyError as e:
                        print(f"Lỗi: Dữ liệu không đầy đủ {e}. Bỏ qua hành động: {action}")

            is_replaying = False
            messagebox.showinfo("Phát Lại", "Đã hoàn thành phát lại!")

        threading.Thread(target=replay).start()

    except Exception as e:
        print(f"Lỗi khi phát lại hành động: {e}")
        print(traceback.format_exc())


def stop_replay():
    """Dừng phát lại khẩn cấp."""
    global stop_replay_event
    stop_replay_event.set()
    print("Đã dừng phát lại khẩn cấp.")


def listen_for_hotkey():
    """Lắng nghe tổ hợp phím Ctrl + F10 để dừng phát lại."""

    def on_press(key):
        if key == Key.f10 and any(k == Key.ctrl for k in pressed_keys):
            stop_replay()

    pressed_keys = set()

    def on_key_press(key):
        pressed_keys.add(key)
        on_press(key)

    def on_key_release(key):
        pressed_keys.discard(key)

    with KeyboardListener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()


def main():
    """Giao diện main."""
    global root
    try:
        root = tk.Tk()
        root.title("Ghi và Phát Lại Hành Động Chuột")

        tk.Label(root, text="Ghi và Phát Lại Hành Động Chuột",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        # Frame cho các nút điều khiển main
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        btn_record = tk.Button(control_frame, text="Bắt Đầu Ghi",
                               command=lambda: threading.Thread(target=record_actions).start())
        btn_record.pack(side=tk.LEFT, padx=5)

        btn_stop = tk.Button(control_frame, text="Dừng Ghi", command=stop_recording)
        btn_stop.pack(side=tk.LEFT, padx=5)

        # Frame cho các nút thao tác với file
        file_frame = tk.Frame(root)
        file_frame.pack(pady=5)

        btn_save = tk.Button(file_frame, text="Lưu Hành Động", command=save_actions)
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_load = tk.Button(file_frame, text="Tải Hành Động", command=load_actions)
        btn_load.pack(side=tk.LEFT, padx=5)

        # Frame cho nút phát lại
        replay_frame = tk.Frame(root)
        replay_frame.pack(pady=5)

        btn_replay = tk.Button(replay_frame, text="Phát Lại Hành Động",
                               command=lambda: threading.Thread(target=replay_actions, args=(root,)).start())
        btn_replay.pack()

        btn_stop_replay = tk.Button(replay_frame, text="Dừng Phát Lại", command=stop_replay)
        btn_stop_replay.pack(pady=5)

        # Chạy luồng lắng nghe hotkey
        threading.Thread(target=listen_for_hotkey, daemon=True).start()

        root.mainloop()
    except Exception as e:
        print(f"Lỗi trong giao diện main: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()