import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.simpledialog as simpledialog
import tkinter.filedialog as filedialog
import os
import random
class MemeLangError(Exception):
    def __init__(self, line, message):
        super().__init__(f"[밈랭 오류] {line}번째 줄: {message}")
        self.line = line
        self.message = message


def execute_code(self, code_lines):
    output = ""

    # =========================
    # 상태
    # =========================
    상태_슬롯 = {
        "주머니": 0,
        "가방": 0,
        "손": 0
    }

    선택_슬롯 = "주머니"
    현재_줄 = 0

    반복_스택 = []
    조건_스택 = [{
        "실행중": True,
        "이미_실행됨": False
    }]

    한글_숫자 = {
        "한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5,
        "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9, "열": 10,
        "서른": 30, "마흔": 40, "쉰": 50, "예순": 60, "일흔": 70
    }

    밈에러 = [
        "와트 이스 디스?",
        "뭐..뭐요?",
        "무 무슨"
    ]

    # =========================
    # 유틸
    # =========================
    def 실행가능():
        return all(c["실행중"] for c in 조건_스택)

    def 조건_판단(조건식, 값):
        if 조건식 == "":
            return 값 == 0
        if 조건식.startswith(">"):
            return 값 > int(조건식[1:])
        if 조건식.startswith("<"):
            return 값 < int(조건식[1:])
        if 조건식.startswith("=="):
            return 값 == int(조건식[2:])
        if 조건식.startswith("!="):
            return 값 != int(조건식[2:])
        raise MemeLangError(현재_줄 + 1, f"알 수 없는 조건식 '{조건식}'")

    # =========================
    # 실행 루프
    # =========================
    while 현재_줄 < len(code_lines):
        줄 = code_lines[현재_줄].strip()
        line_no = 현재_줄 + 1

        # 빈 줄 / 주석
        if not 줄 or 줄.startswith("#"):
            현재_줄 += 1
            continue

        parts = 줄.split()

        # =====================
        # 슬롯 선택
        # =====================
        if len(parts) == 2 and parts[1] == "집다":
            if parts[0] not in 상태_슬롯:
                raise MemeLangError(line_no, f"'{parts[0]}' 은(는) 존재하지 않는 슬롯입니다")
            if 실행가능():
                선택_슬롯 = parts[0]
            현재_줄 += 1

        # =====================
        # 증가 / 감소
        # =====================
        elif 줄 == "집는다":
            if 실행가능():
                상태_슬롯[선택_슬롯] += 1
            현재_줄 += 1

        elif 줄 == "놓는다":
            if 실행가능():
                상태_슬롯[선택_슬롯] -= 1
            현재_줄 += 1

        # =====================
        # 출력
        # =====================
        elif 줄.startswith("말한다"):
            if 실행가능():
                내용 = 줄[3:].strip()
                if not 내용:
                    raise MemeLangError(line_no, "말한다 뒤에 출력할 내용을 써야 합니다")
                if 내용 in 상태_슬롯:
                    output += str(상태_슬롯[내용]) + "\n"
                else:
                    output += 내용 + "\n"
            현재_줄 += 1

        # =====================
        # 입력
        # =====================
        elif 줄.startswith("묻는다"):
            if len(parts) == 1:
                raise MemeLangError(line_no, "묻는다 뒤에 물어볼 말을 써야 합니다")
            if 실행가능():
                프롬프트 = 줄[3:].strip()
                입력 = simpledialog.askstring("입력", 프롬프트)
                if 입력 and 입력.isdigit():
                    상태_슬롯[선택_슬롯] = int(입력)
            현재_줄 += 1

        # =====================
        # 반복 시작
        # =====================
        elif 줄.endswith("번"):
            반복_대상 = parts[0]

            if 반복_대상 in 상태_슬롯:
                횟수 = 상태_슬롯[반복_대상]
            else:
                횟수 = 한글_숫자.get(반복_대상, None)

            if 횟수 is None:
                raise MemeLangError(line_no, f"반복 횟수를 알 수 없습니다: '{반복_대상}'")

            if 횟수 <= 0:
                raise MemeLangError(line_no, f"반복 횟수가 {횟수} 입니다. 이건 반복이 아닙니다")

            반복_스택.append({
                "시작": 현재_줄 + 1,
                "남음": 횟수
            })
            현재_줄 += 1

        # =====================
        # 반복 끝
        # =====================
        elif 줄 == "다시한다":
            if not 반복_스택:
                raise MemeLangError(line_no, "다시한다를 썼지만 반복이 시작된 적이 없습니다")

            반복_스택[-1]["남음"] -= 1
            if 반복_스택[-1]["남음"] > 0:
                현재_줄 = 반복_스택[-1]["시작"]
            else:
                반복_스택.pop()
                현재_줄 += 1

        # =====================
        # 조건 시작 (if)
        # =====================
        elif 줄 == "확인한다":
            상위 = 조건_스택[-1]
            실행 = 상위["실행중"] and (상태_슬롯[선택_슬롯] == 0)

            조건_스택.append({
                "실행중": 실행,
                "이미_실행됨": 실행
            })
            현재_줄 += 1

        # =====================
        # elif
        # =====================
        elif 줄.startswith("아니인가?"):
            if len(조건_스택) == 1:
                raise MemeLangError(line_no, "아니인가? 는 확인한다 없이 사용할 수 없습니다")

            조건식 = 줄.replace("아니인가?", "")
            현재 = 조건_스택[-1]

            if 현재["이미_실행됨"]:
                현재["실행중"] = False
            else:
                값 = 상태_슬롯[선택_슬롯]
                실행 = 조건_판단(조건식, 값)
                현재["실행중"] = 실행
                if 실행:
                    현재["이미_실행됨"] = True

            현재_줄 += 1

        # =====================
        # else
        # =====================
        elif 줄 == "아니다":
            if len(조건_스택) == 1:
                raise MemeLangError(line_no, "아니다 는 확인한다 없이 사용할 수 없습니다")

            현재 = 조건_스택[-1]
            현재["실행중"] = not 현재["이미_실행됨"]
            현재["이미_실행됨"] = True
            현재_줄 += 1

        # =====================
        # 조건 끝
        # =====================
        elif 줄 == "끝확인":
            if len(조건_스택) == 1:
                raise MemeLangError(line_no, "끝확인에 대응하는 확인한다가 없습니다")
            조건_스택.pop()
            현재_줄 += 1

        # =====================
        # 알 수 없는 문법
        # =====================
        else:
            raise MemeLangError(
                line_no,
                random.choice(밈에러) + f": '{줄}'"
            )

    return output
class LineNumbers(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.text_widget.bind("<KeyRelease>", self.redraw)
        self.text_widget.bind("<MouseWheel>", self.redraw)
        self.text_widget.bind("<Button-1>", self.redraw)

    def redraw(self, event=None):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(
                30, y,
                anchor="ne",
                text=linenum,
                fill="#858585",
                font=("Consolas", 11)
            )
            i = self.text_widget.index(f"{i}+1line")

class memelangediter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Windowwindowwindow")
        self.작성한_코드=tk.StringVar()
        
        self.create_widgets()
        self.root.mainloop()
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MemeLang Files", "*.memelang"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert(tk.END, file_content)
    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".memelang", filetypes=[("MemeLang Files", "*.memelang"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get('1.0', tk.END))
    def run_file(self):
        def show_output(output):
            output_window = tk.Toplevel(self.root)
            output_window.title("출력 결과")
            output_text = tk.Text(output_window, wrap="word", font=("Consolas", 12))
            output_text.pack(expand=True, fill="both")
            output_text.insert(tk.END, output)
            output_text.configure(state="disabled")
        #코드를 한줄 한줄 리스트로 읽어 오기
        code_lines = [line.strip() for line in self.text_area.get('1.0', tk.END).splitlines() if line.strip()]
        #코드 실행
        output = ""
        try:
            output = execute_code(self, code_lines)
        except Exception as e:
            messagebox.showerror("오류", f"코드 실행 중 오류가 발생했습니다:\n{e}")
            return
        show_output(output)
    def create_widgets(self):
        self.root.configure(bg="#f6f5f3")
        self.card = tk.Frame(self.root, bg="white")
        self.card.pack(padx=20, pady=20)

        self.title = tk.Label(
            self.card,
            text="밈랭 에디터",
            font=("Pretendard", 22, "bold"),
            bg="white"
        )
        self.title.pack(pady=(15, 5))

        self.subtitle = tk.Label(
            self.card,
            text="한글로 작성하는 프로그래밍 언어",
            font=("Pretendard", 11),
            bg="white",
            fg="#666"
        )
        self.subtitle.pack(pady=(0, 10))

        # 버튼
        self.button_frame = tk.Frame(self.card, bg="white")
        self.button_frame.pack(pady=5)

        tk.Button(self.button_frame, text="📂 열기", command=self.open_file).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="💾 저장", command=self.save_file).pack(side="left", padx=5)
        tk.Button(self.button_frame, text="▶ 실행", command=self.run_file).pack(side="left", padx=5)

        # 에디터 영역
        self.editor_frame = tk.Frame(self.card, bg="#1e1e1e")
        self.editor_frame.pack(padx=15, pady=15)

        self.text_area = tk.Text(
            self.editor_frame,
            width=65,
            height=20,
            font=("Consolas", 12),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            relief="flat"
        )
        self.text_area.pack(side="right")
        print([line.strip() for line in self.text_area.get('1.0', tk.END).splitlines() if line.strip()])
        self.line_numbers = LineNumbers(
            self.editor_frame,
            self.text_area,
            width=40,
            bg="#252526",
            highlightthickness=0
        )
        self.line_numbers.pack(side="left", fill="y")

        self.line_numbers.redraw()
    


if __name__ == "__main__":
    app = memelangediter()