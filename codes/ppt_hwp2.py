import os
import subprocess

def pdf(input_file, output_dir=None):
    """
    LibreOffice를 사용하여 입력 파일을 PDF로 변환합니다.

    Args:
        input_file (str): 원본 파일 경로
        output_dir (str, optional): 변환된 PDF 파일을 저장할 디렉토리. 기본값은 입력 파일의 디렉토리
    """
    # 입력 파일 유효성 확인
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_file}")
    
    # 출력 디렉토리 설정
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(input_file))

    os.makedirs(output_dir, exist_ok=True)

    try:
        # LibreOffice CLI를 사용하여 PDF로 변환
        subprocess.run([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_file
        ], check=True)

        # 출력 파일 확인
        base_name = os.path.basename(input_file)
        pdf_file = os.path.join(output_dir, os.path.splitext(base_name)[0] + ".pdf")

        if os.path.exists(pdf_file):
            print(f"PDF 변환 성공: {pdf_file}")
        else:
            print("PDF 변환이 실패했습니다. 출력 파일을 찾을 수 없습니다.")

        return pdf_file
    except subprocess.CalledProcessError as e:
        print(f"LibreOffice 변환 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"예기치 않은 오류가 발생했습니다: {e}")




import win32com.client as win32
import time
import pyautogui
import threading

def hwp_to_pdf(hwp_file_path, delay=10):
    """
    HWP 파일을 PDF로 변환하는 함수. 보안 팝업을 감지하고 처리.
    :param delay: 팝업 창 대기 시간(초)
    """
    pdf_file_path = os.path.splitext(hwp_file_path)[0] + ".pdf"
    try:
        # 한글 프로그램 실행
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")  # 보안 모듈 적용
        hwp.XHwpWindows.Item(0).Visible = False  # 한글 GUI 숨기기

        # 팝업 처리 스레드 실행 (delay 값 전달)
        popup_thread = threading.Thread(target=handle_hwp_popup, args=(delay,))
        popup_thread.start()

        # HWP 파일 열기
        hwp.Open(hwp_file_path)

        # PDF 저장 설정
        hwp.HAction.GetDefault("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.HParameterSet.HFileOpenSave.filename = pdf_file_path  # 저장할 PDF 경로
        hwp.HParameterSet.HFileOpenSave.Format = "PDF"  # 저장 형식
        hwp.HParameterSet.HFileOpenSave.Attributes = 16384  # PDF 속성 설정
        hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)

        print(f"PDF로 저장 완료: {pdf_file_path}")

        return pdf_file_path
    except Exception as e:
        print(f"에러 발생: {e}")

    finally:
        # HWP 종료
        hwp.Quit()
        popup_thread.join()  # 팝업 처리 스레드가 종료될 때까지 기다림

def handle_hwp_popup(delay=10):
    """
    지정된 시간(기본값: 10초) 후 'y' 키를 누릅니다.
    :param delay: 대기 시간(초)
    """
    print(f"{delay}초 대기 중...")
    time.sleep(delay)  # 지정된 시간 동안 대기
    pyautogui.press('y')  # 'y' 키 입력
    print("'y' 키 입력 완료.")



'''
# 사용 예제 (대기 시간 5초 설정)
hwp_file = r"C:/Users/LG/miniconda3/envs/BLNK/codes/check/just/과연x.hwpx"
pdf_file = r"C:/Users/LG/miniconda3/envs/BLNK/codes/check/just/과연x.pdf"
hwp_to_pdf(hwp_file, pdf_file, delay=2)
'''



if __name__ == "__main__":
    file = "C:/Users/LG/miniconda3/envs/BLNK/codes/check/just/과연x.hwpx"
    pdf(input_file=file)



    