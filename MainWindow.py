import ctypes
import threading
import time

import pyfirmata
import serial.tools.list_ports
from playsound import playsound
from PyQt6.QtCore import QEventLoop, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QGuiApplication, QIcon, QIntValidator
from PyQt6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
                             QFrame, QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QMainWindow, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Timer")
        # set app icon
        app_icon = QIcon()
        app_icon.addFile('icon/t.png', QSize(16, 16))
        app_icon.addFile('icon/t.png', QSize(24, 24))
        app_icon.addFile('icon/t.png', QSize(32, 32))
        app_icon.addFile('icon/t.png', QSize(48, 48))
        app_icon.addFile('icon/t.png', QSize(256, 256))
        self.setWindowIcon(app_icon)
        self.setObjectName("MainWindow")
        self.resize(600, 600)
        outer_layout = QHBoxLayout()
        left_layout = QGridLayout()
        right_layout = QHBoxLayout()

        # HEADER TEXT - "Control"
        # //////////////////////////////////////////////
        self.headerText = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setUnderline(True)
        self.headerText.setFont(font)
        self.headerText.setObjectName("headerText")
        self.headerText.setText("Control")
        left_layout.addWidget(self.headerText, 0, 0, 1, 1)

        # font for checkbox labels
        font = QFont()
        font.setPointSize(8)

        # PLAY CHECKBOX
        self.checkbox_play = QCheckBox()
        self.checkbox_play.setObjectName("play_checkbox")
        # play checkbox label
        self.label_play = QLabel()
        self.label_play.setFont(font)
        self.label_play.setObjectName("label")
        self.label_play.setText("Start")

        # USB CHECKBOX
        self.checkbox_usb = QCheckBox()
        self.checkbox_usb.setObjectName("checkbox_usb")
        # usb checkbox label
        self.label_usb = QLabel()
        self.label_usb.setFont(font)
        self.label_usb.setObjectName("label_usb")
        self.label_usb.setText("USB")

        # STOPWATCH CHECKBOX
        self.checkbox_stopwatch = QCheckBox()
        self.checkbox_stopwatch.setObjectName("checkbox_stopwatch")
        # stopwatch checkbox label
        self.label_stopwatch = QLabel()
        self.label_stopwatch.setFont(font)
        self.label_stopwatch.setObjectName("stopwatch_label")
        self.label_stopwatch.setText("Stopwatch")

        # LAPS CHECKBOX
        self.checkbox_laps = QCheckBox()
        self.checkbox_laps.setObjectName("checkbox_laps")
        # laps checkbox label
        self.label_checkbox_laps = QLabel()
        self.label_checkbox_laps.setFont(font)
        self.label_checkbox_laps.setObjectName("stopwatch_label")
        self.label_checkbox_laps.setText("Laps")

        # LAYOUT FOR PLAY, STOPWATCH, LAPS, USB - LABELS AND CHECKBOXES
        checkbox_layout = QFormLayout()
        checkbox_layout.addRow(self.label_play, self.checkbox_play)
        checkbox_layout.addRow(self.label_stopwatch, self.checkbox_stopwatch)
        checkbox_layout.addRow(self.label_checkbox_laps, self.checkbox_laps)
        checkbox_layout.addRow(self.label_usb, self.checkbox_usb)
        left_layout.addLayout(checkbox_layout, 1, 0, 2, 1)

        # PLAY AND CANCEL BUTTONS
        # //////////////////////////////////////////////
        self.play_button = QPushButton()
        self.play_button.setObjectName("button")
        self.play_button.setText("Start")
        self.cancel_button = QPushButton()
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setText("Cancel")
        # play and cancel button layout
        play_button_layout = QVBoxLayout()
        play_button_layout.addWidget(self.play_button)
        play_button_layout.addWidget(self.cancel_button)
        left_layout.addLayout(play_button_layout, 1, 2)

        # TIMER INPUT FIELDS
        # //////////////////////////////////////////////
        self.label_sec = QLabel()
        font = QFont()
        font.setPointSize(9)
        self.label_sec.setFont(font)
        self.label_sec.setObjectName("label")
        self.label_sec.setText("Sec")
        # timer input field
        self.input_sec = QLineEdit()
        self.input_sec.setObjectName("sec_input")
        self.input_sec.setStyleSheet(
            "border-radius: 5px; color: red; border: 1px solid lightgray")
        # self.sec_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_sec.setPlaceholderText("Enter Seconds")
        self.input_sec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_sec.setMinimumHeight(20)
        validator = QIntValidator()
        self.input_sec.setValidator(validator)

        # ADD SEC INPUT TO SECONDS/LAPS LAYOUT
        timer_input_layout = QFormLayout()
        timer_input_layout.addRow(self.label_sec, self.input_sec)

        # LAPS INPUT FIELDS
        # //////////////////////////////////////////////
        self.label_laps = QLabel()
        font = QFont()
        font.setPointSize(9)
        self.label_laps.setFont(font)
        self.label_laps.setObjectName("label_laps")
        self.label_laps.setText("Laps")
        # LAPS INPUT
        self.laps = QLineEdit()
        self.laps.setObjectName("laps")
        self.laps.setStyleSheet(
            "border-radius: 5px; color: red; border: 1px solid lightgray")
        self.laps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.laps.setPlaceholderText("Enter laps")
        self.laps.setMinimumHeight(20)
        validator = QIntValidator()
        self.laps.setValidator(validator)
        # ADD LAPS TO SECONDS/LAPS LAYOUT
        timer_input_layout.addRow(self.label_laps, self.laps)

        left_layout.addLayout(timer_input_layout, 2, 1, 1, 2)

        # BIG TIMER MAIN WINDOW
        # //////////////////////////////////////////////
        self.big_timer = QLabel()
        self.big_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.big_timer.setObjectName("timer1")
        self.big_timer.setFont(QFont("Arial", 100))
        self.big_timer.setText("<h1> 0 </h1>")
        right_layout.addWidget(self.big_timer)

        # OPEN BIG TIMER BUTTON
        # //////////////////////////////////////////////
        self.big_timer_window_button = QPushButton()
        self.big_timer_window_button.setObjectName("big_timer_window")
        self.big_timer_window_button.setText("Fullscreen Timer")
        left_layout.addWidget(self.big_timer_window_button, 4, 0, 1, 3)

        # OPEN SECOND BIG TIMER
        self.big_timer_window_button2 = QPushButton()
        self.big_timer_window_button2.setObjectName("big_timer_window")
        self.big_timer_window_button2.setText("Fullscreen Timer 2")
        left_layout.addWidget(self.big_timer_window_button2, 5, 0, 1, 3)

        # SEPERATOR LINE
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setObjectName("line")
        left_layout.addWidget(self.line, 6, 0, 1, 4)

        # ARDUINO
        # //////////////////////////////////////////////
        self.label_arduino = QLabel()
        font = QFont()
        font.setPointSize(10)
        self.label_arduino.setFont(font)
        self.label_arduino.setObjectName("arduinoText")
        self.label_arduino.setText("Arduino")
        # configure arduino button
        self.conf_arduino_button = QPushButton()
        self.conf_arduino_button.setObjectName("confArduinoButton")
        self.conf_arduino_button.setText("Configure")
        left_layout.addWidget(self.label_arduino, 7, 0, 1, 4)
        left_layout.addWidget(self.conf_arduino_button, 8, 0, 1, 2)

        # SEPERATOR LINE
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setObjectName("line")
        left_layout.addWidget(self.line, 9, 0, 1, 4)

        # LABEL, BUTTON SPLIT TIME / PAUSE FOR LAPS
        # //////////////////////////////////////////////
        # LABEL
        self.label_laps_big_text = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setUnderline(True)
        self.label_laps_big_text.setFont(font)
        self.label_laps_big_text.setObjectName("lapsText")
        self.label_laps_big_text.setText("Laps")

        # 2 RIDERS CHECKBOX
        self.checkbox_two_riders = QCheckBox()
        self.checkbox_two_riders.setObjectName("checkbox_two_riders")
        self.checkbox_two_riders.setToolTip(
            "Check if 2 riders are racing at the same time")
        # 2 RIDERS CHECKBOX LABEL
        self.label_two_riders = QLabel()
        font = QFont()
        font.setPointSize(8)
        self.label_two_riders.setFont(font)
        self.label_two_riders.setObjectName("label_two_riders")
        self.label_two_riders.setText("2 Riders")

        # BUTTONS
        self.lap_button = QPushButton()
        self.lap_button.setObjectName("pause_button")
        self.lap_button.setDisabled(True)
        self.lap_button.setText("Split Time / Lap")
        self.lap_button2 = QPushButton()
        self.lap_button2.setObjectName("pause_button")
        self.lap_button2.setDisabled(True)
        self.lap_button2.setText("Split Time / Lap 2")

        # LAPS LAYOUT
        lap_layout = QFormLayout()
        lap_layout.addRow(self.label_laps_big_text)
        lap_layout.addRow(self.label_two_riders, self.checkbox_two_riders)
        lap_layout.addRow(self.lap_button)
        lap_layout.addRow(self.lap_button2)
        left_layout.addLayout(lap_layout, 10, 0, 1, 2)

        # NUMBERS FOR SPLIT TIME FILES
        # Rider 1
        self.rider_one_number = QLineEdit()
        self.rider_one_number.setStyleSheet(
            "border-radius: 5px; color: red; border: 1px solid lightgray")
        self.rider_one_number.setPlaceholderText("Enter Rider")
        self.rider_one_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rider_one_number.setMinimumHeight(20)
        # Rider 2
        self.rider_two_number = QLineEdit()
        self.rider_two_number.setStyleSheet(
            "border-radius: 5px; color: red; border: 1px solid lightgray")
        self.rider_two_number.setPlaceholderText("Enter Rider")
        self.rider_two_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rider_two_number.setMinimumHeight(20)

        self.enter_rider_info = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setUnderline(True)
        self.enter_rider_info.setFont(font)
        self.enter_rider_info.setText("Enter Rider info")

        rider_layout = QFormLayout()

        rider_layout.addRow(self.enter_rider_info)
        rider_layout.addRow(QLabel("Name or number"))
        rider_layout.addRow(self.rider_one_number)
        rider_layout.addRow(self.rider_two_number)
        left_layout.addLayout(rider_layout, 10, 2, 1, 2)

        # STRETCH LEFT LAYOUT
        self.riders_switch_position = QPushButton()
        self.riders_switch_position.setText("Riders Switched Position")
        self.riders_switch_position.setEnabled(False)
        left_bottom_layout = QVBoxLayout()
        left_bottom_layout.addWidget(self.riders_switch_position)
        left_layout.addLayout(left_bottom_layout, 11, 0, 10, 3)

        outer_layout.addLayout(left_layout, 1)
        outer_layout.addLayout(right_layout, 6)

        main_widget = QWidget()
        main_widget.setLayout(outer_layout)
        self.setCentralWidget(main_widget)

        # BUTTON CLICK
        # //////////////////////////////////////////////
        self.play_button.clicked.connect(self.button_click)
        self.cancel_button.clicked.connect(self.button_click)
        self.big_timer_window_button.clicked.connect(self.button_click)
        self.big_timer_window_button2.clicked.connect(self.button_click)
        self.conf_arduino_button.clicked.connect(self.button_click)
        self.lap_button.clicked.connect(self.button_click)
        self.lap_button2.clicked.connect(self.button_click)
        self.riders_switch_position.clicked.connect(self.button_click)

        self.input_sec.textChanged.connect(self.set_big_timer_label_text)
        self.checkbox_laps.stateChanged.connect(self.set_lap_button_state)
        self.laps.textChanged.connect(self.set_big_timer_laps)
        self.checkbox_two_riders.stateChanged.connect(
            self.disable_riders_switched_position_button)

        # FLAGS AND VARIABLES
        # //////////////////////////////////////////////
        self.break_loop = False
        self.septimewindow = False
        self.septimewindow2 = False
        self.stopwatch_flag = False
        self.big_window_stopwatch_flag1 = False
        self.big_window_stopwatch_flag2 = False
        self.laps_amount = 0
        self.laps_amount2 = 0
        self.wheels = 0
        self.arduino_read = True
        self.arduino_read2 = True
        self.split_time1 = False
        self.split_time2 = False
        # Ui_MainWindow.number1Value = self.number1.text()

    # FUNCTIONS
    # //////////////////////////////////////////////

    # ERROR MSG
    # -----------------
    def error_msg(self, text):
        self.error_dialog = QMessageBox()
        self.error_dialog.warning(self, "Error", text)

    def break_loop_and_send_error_msg(self, arg0):
        self.break_loop = True
        self.error_msg(arg0)
        self.set_cancel_button_text()

    # LOOP TIMER
    # -----------------
    def loop(self, time):
        self.loop1 = QEventLoop()
        self.tm = QTimer.singleShot(time, self.loop1.quit)
        self.loop1.exec()

    # PLAY SOUND
    # -----------------
    def play_sound(self, str):
        threading.Thread(target=playsound, args=(str,), daemon=True).start()

    # SET TEXT
    # -----------------
    # CANCEL BUTTON
    def set_cancel_button_text(self):
        if self.stopwatch_flag:
            self.cancel_button.setText("Stop")
        else:
            self.cancel_button.setText("Reset")
            self.cancel_button.setStyleSheet("background-color: yellow")

    # DISABLE Riders Switched Position BUTTON WHILE NOT ACTIVE
    def disable_riders_switched_position_button(self):
        if self.checkbox_two_riders.isChecked():
            self.riders_switch_position.setEnabled(True)
        else:
            self.riders_switch_position.setEnabled(False)

    # LAP BUTTON

    def set_lap_button_state(self):
        if self.checkbox_laps.isChecked():
            self.lap_button.setEnabled(True)
            self.lap_button2.setEnabled(True)
            self.big_timer_window_button.setText("Lap Fullscreen Timer")
            self.big_timer_window_button2.setText("Lap Fullscreen Timer 2")
        else:
            self.big_timer_window_button.setText("Fullscreen Timer")
            self.big_timer_window_button2.setText("Fullscreen Timer 2")
            self.lap_button.setEnabled(False)
            self.lap_button2.setEnabled(False)
        if self.septimewindow:
            self.big_timer_window_button.click()
        if self.septimewindow2:
            self.big_timer_window_button2.click()

    # BIG TIMER LABEL
    def set_big_timer_label_text(self, e):
        self.big_timer.setText("<h1>" + e + "</h1>")
        if self.septimewindow:
            self.big_window.set_timer_text("<h1>" + e + "</h1>")
        if self.septimewindow2:
            self.big_window2.set_timer_text("<h1>" + e + "</h1>")

    # BIG TIMER LAPS
    def set_big_timer_laps(self):
        if self.stopwatch_flag == False:
            if self.septimewindow:
                self.big_window.set_laps(self.laps.text())
            if self.septimewindow2:
                self.big_window2.set_laps(self.laps.text())

    # OPEN FILES TO WRITE
    # //////////////////////////////////////////////
    def open_split_time_files(self):
        current_time = time.localtime()
        if self.septimewindow:
            self.main_straight_file = open(
                f"results/1st-({current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday})({current_time.tm_hour}-{current_time.tm_min}-{current_time.tm_sec})-({self.rider_one_number.text()}).txt", "a")

        if self.septimewindow2:
            self.second_straight_file = open(
                f"results/2nd-({current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday})({current_time.tm_hour}-{current_time.tm_min}-{current_time.tm_sec})-({self.rider_two_number.text()}).txt", "a")

    # TRY CLOSING FILES WHEN 'STOP' PRESSED
    def try_closing_split_time_files(self):
        try:
            self.main_straight_file.close()
        except:
            pass
        try:
            self.second_straight_file.close()
        except:
            pass

    # WRITE SPLIT TIMES TO FILES
    def write_split_times_to_file(self, straight_number, finish=False, finish_min=0, finish_sec=0):
        if straight_number == 1 and finish:
            self.main_straight_file.write(
                str(f"FINISH: {finish_min:02d}:{finish_sec}"))
            self.main_straight_file.close()
        elif straight_number == 1 and not finish:
            self.main_straight_file.write(
                str(f"{self.laps_for_split_times - self.laps_amount}: {finish_min:02d}:{finish_sec}"))
            self.main_straight_file.write("\n")

        if straight_number == 2 and finish:
            self.second_straight_file.write(
                str(f"FINISH: {finish_min:02d}:{finish_sec}"))
            self.second_straight_file.close()
        elif straight_number == 2 and not finish:
            self.second_straight_file.write(
                str(f"{self.laps_for_split_times - self.laps_amount2}: {finish_min:02d}:{finish_sec}"))
            self.second_straight_file.write("\n")

    # RESET LABELS
    # //////////////////////////////////////////////
    def reset_labels_to_sec_input(self):
        self.big_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.big_timer.setText("<h1>" + self.input_sec.text() + "</h1>")
        if self.septimewindow:
            if self.laps.text():
                self.big_window.set_laps(self.laps.text())
            else:
                self.big_window.set_font_size_to_stopwatch(3)
            if self.big_window.split_time:
                self.big_window.split_time.setParent(None)
            self.big_window.set_timer_text(self.input_sec.text())
        if self.septimewindow2:
            if self.laps.text():
                self.big_window2.set_laps(self.laps.text())
            else:
                self.big_window2.set_font_size_to_stopwatch(3)
            if self.big_window2.split_time:
                self.big_window2.split_time.setParent(None)
            self.big_window2.set_timer_text(self.input_sec.text())

    # SET ARDUINO COM PORT
    # -----------------
    def set_arduino_port(self, str):
        self.board = pyfirmata.Arduino(str)
        it = pyfirmata.util.Iterator(self.board)
        it.start()
        self.digital_input9 = self.board.get_pin("d:9:i")
        self.digital_input10 = self.board.get_pin("d:10:i")
        self.digital_output5 = self.board.get_pin("d:5:o")
        self.digital_output6 = self.board.get_pin("d:6:o")
        self.label_arduino.setText("Arduino <b>OK!</b>")

    def set_arduino_read_false_true1(self):
        self.arduino_read = None
        self.loop(1000)
        self.arduino_read = True

    def set_arduino_read_false_true2(self):
        self.arduino_read2 = None
        self.loop(1000)
        self.arduino_read2 = True

    def switch_arduino_read_value(self):
        self.split_time1 = not self.split_time1
        self.split_time2 = not self.split_time2

    # CLOSE WINDOW IF ESC PRESSED
    # -----------------

    def close_window1(self):
        self.septimewindow = False

    def close_window2(self):
        self.septimewindow2 = False

    # BUTTON CLICK EVENTS
    # //////////////////////////////////////////////

    def start_button(self):
        if self.input_sec.text().isnumeric() and self.checkbox_play.isChecked():
            self.break_loop = False
            if self.checkbox_usb.isChecked():
                try:
                    if self.board:
                        pass
                except:
                    self.break_loop_and_send_error_msg(
                        "Arduino not configured ")
            if self.checkbox_laps.isChecked() and (
                self.laps.text()
                and int(self.laps.text()) < 1
                or not self.laps.text()
            ):
                self.break_loop_and_send_error_msg(
                    "Laps need to be greater than 0")
            if self.laps.text() and not self.checkbox_laps.isChecked():
                self.break_loop_and_send_error_msg("'Laps' checkbox unchecked")
            self.play_button.setEnabled(False)
            if self.checkbox_laps.isChecked() and self.checkbox_stopwatch.isChecked():
                self.open_split_time_files()
            self.timer()

        else:
            self.error_msg("'Start' checkbox not clicked or no number")

    def button_click(self):
        sender = self.sender().text()
        print(f"{sender} was pressed")

        if sender == "Start":
            self.start_button()

        if sender == "Cancel":
            self.break_loop = True
            self.set_cancel_button_text()

        if sender == "Stop":
            self.break_loop = True
            self.stopwatch_flag = False
            self.stop_stopwatch()
            self.try_closing_split_time_files()

        if sender == "Reset":
            self.reset_labels_to_sec_input()
            self.play_button.setEnabled(True)
            self.cancel_button.setText("Cancel")
            self.cancel_button.setStyleSheet("")

        if sender == "Fullscreen Timer":
            self.big_window = SeperateTimerWindow()
            if self.input_sec:
                self.big_window.set_timer_text(self.input_sec.text())
            self.big_window.setWindowTitle("Timer 1")
            self.big_window.show()
            self.big_window.closed.connect(self.close_window1)
            self.septimewindow = True

        if sender == "Fullscreen Timer 2":
            self.big_window2 = SeperateTimerWindow()
            if self.input_sec:
                self.big_window2.set_timer_text(self.input_sec.text())
            self.big_window2.setWindowTitle("Timer 2")
            self.big_window2.show()
            self.big_window2.closed.connect(self.close_window2)
            self.septimewindow2 = True

        if sender == "Lap Fullscreen Timer":
            self.big_window = LapsSeperateTimerWindow()
            self.big_window.set_laps(self.laps.text())
            if self.input_sec:
                self.big_window.set_timer_text(self.input_sec.text())
            self.big_window.setWindowTitle("Timer 1")
            self.big_window.show()
            self.big_window.closed.connect(self.close_window1)
            self.septimewindow = True

        if sender == "Lap Fullscreen Timer 2":
            self.big_window2 = LapsSeperateTimerWindow()
            self.big_window2.set_laps(self.laps.text())
            if self.input_sec:
                self.big_window2.set_timer_text(self.input_sec.text())
            self.big_window2.setWindowTitle("Timer 2")
            self.big_window2.show()
            self.big_window2.closed.connect(self.close_window2)
            self.septimewindow2 = True

        if sender == "Configure":
            self.config_window = ConfigureUSBWindow(self)
            self.config_window.show()

        if sender == "Split Time / Lap":
            self.stopwatch_split_time()

        if sender == "Split Time / Lap 2":
            self.stopwatch_split_time2()

        if sender == "Riders Switched Position":
            self.switch_arduino_read_value()
            print(self.arduino_read)
            print(self.arduino_read2)

    # COUNTDOWN TIMER
    # //////////////////////////////////////////////
    def timer(self):
        t = int(self.input_sec.text()) + int(time.time())
        i = t - int(time.time())

        # Display mm:ss timeformat
        while i >= 60:
            i = t - int(time.time())
            min, sec = divmod(i, 60)
            output = f"{min:02d}:{sec:>2}"
            if self.break_loop == True:
                break
            self.big_timer.setText("<h1>" + str(output) + "</h1>")
            if self.septimewindow:
                self.big_window.set_timer_text(str(output))
            if self.septimewindow2:
                self.big_window2.set_timer_text(str(output))
            self.loop(500)
            i -= 1

        # Display ss timeformat
        while i >= 0:
            i = t - int(time.time())
            if self.break_loop == True:
                break
            self.big_timer.setText("<h1>" + str(i) + "</h1>")
            if self.septimewindow:
                self.big_window.set_timer_text(str(i))
            if self.septimewindow2:
                self.big_window2.set_timer_text(str(i))
            if i <= 0:
                break
            if 0 < i < 6 or i == 50 or i == 30 or i == 10:
                self.play_sound("mp3/beep.mp3")
                self.loop(1000)
            else:
                self.loop(500)
            i -= 1

        if i <= 0:
            self.start_time = time.time()
            if self.checkbox_usb.isChecked():
                self.digital_output5.write(1)
                self.digital_output6.write(1)
            self.play_sound('mp3/beep-long.mp3')
            if self.septimewindow or self.septimewindow2:
                if self.septimewindow:
                    self.big_window.finish_background_green()
                if self.septimewindow2:
                    self.big_window2.finish_background_green()
                self.loop(1000)
                if self.septimewindow:
                    self.big_window.finish_background_reset()
                if self.septimewindow2:
                    self.big_window2.finish_background_reset()
            else:
                self.loop(1000)
            if self.checkbox_usb.isChecked():
                self.digital_output5.write(0)
                self.digital_output6.write(0)
            if self.checkbox_stopwatch.isChecked():
                self.stopwatch_flag = True
                self.stopwatch()
        if not self.checkbox_stopwatch.isChecked():
            self.cancel_button.setText("Reset")
            self.cancel_button.setStyleSheet("background-color: yellow")

    # STOPWATCH
    # //////////////////////////////////////////////
    def stopwatch(self):
        self.min = 0
        self.big_timer.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.big_timer.setStyleSheet('padding-left: 30px')
        self.set_cancel_button_text()

        if self.checkbox_laps.isChecked():
            self.laps_for_split_times = int(self.laps.text())

        if self.septimewindow:
            self.big_window.set_font_size_to_stopwatch()
            self.big_window_stopwatch_flag1 = True
            if self.checkbox_laps.isChecked():
                self.laps_amount = int(self.laps.text())
            else:
                self.laps_amount = 0

        if self.septimewindow2:
            self.big_window2.set_font_size_to_stopwatch()
            self.big_window_stopwatch_flag2 = True
            if self.checkbox_laps.isChecked():
                self.laps_amount2 = int(self.laps.text())
                print(self.laps_amount2)
            else:
                self.laps_amount2 = 0
                print(self.laps_amount2)

        while self.stopwatch_flag:
            self.elapsed_time = round((time.time() - self.start_time), 2)
            self.min, self.sec = divmod(self.elapsed_time, 60)
            self.min = int(self.min)
            self.sec = "{:.2f}".format(self.sec)
            self.big_timer.setText(
                str(f"{self.min:02d}:{self.sec:>5}"))
            if self.septimewindow and self.big_window_stopwatch_flag1:
                self.big_window.set_timer_text(self.big_timer.text())
            if self.septimewindow2 and self.big_window_stopwatch_flag2:
                self.big_window2.set_timer_text(self.big_timer.text())

            # Split times from ARDUINO - Straight 1
            if self.checkbox_usb.isChecked() and self.elapsed_time > 2 and self.digital_input9.read() == self.arduino_read:
                if self.checkbox_two_riders.isChecked() and self.split_time1:
                    self.stopwatch_split_time()
                    threading.Thread(
                        target=self.set_arduino_read_false_true1, args=(), daemon=True).start()
                    self.split_time1 = False
                elif self.checkbox_two_riders.isChecked() and not self.split_time1:
                    threading.Thread(
                        target=self.set_arduino_read_false_true1, args=(), daemon=True).start()
                    self.split_time1 = True
                    self.big_window.set_split_time("")
                else:
                    self.stopwatch_split_time()
                    threading.Thread(
                        target=self.set_arduino_read_false_true1, args=(), daemon=True).start()

            # Split times from ARDUINO - Straight 2
            if self.checkbox_usb.isChecked() and self.elapsed_time > 2 and self.digital_input10.read() == self.arduino_read2:
                if self.checkbox_two_riders.isChecked() and self.split_time2:
                    self.stopwatch_split_time2()
                    threading.Thread(
                        target=self.set_arduino_read_false_true2, args=(), daemon=True).start()
                    self.split_time2 = False
                elif self.checkbox_two_riders.isChecked() and not self.split_time2:
                    threading.Thread(
                        target=self.set_arduino_read_false_true2, args=(), daemon=True).start()
                    self.split_time2 = True
                    self.big_window2.set_split_time("")
                else:
                    self.stopwatch_split_time2()
                    threading.Thread(
                        target=self.set_arduino_read_false_true2, args=(), daemon=True).start()

            self.loop(100)

    def stopwatch_split_time(self):
        split_min, split_sec = divmod((time.time() - self.start_time), 60)
        split_min = int(split_min)
        split_sec = f"{split_sec:.2f}"
        if self.big_window_stopwatch_flag1:
            if self.laps_amount <= 1:
                self.laps_amount -= 1
                self.stop_stopwatch()

            else:
                self.laps_amount -= 1
                self.laps.setText(str(self.laps_amount))
                if self.septimewindow:
                    self.big_window.set_laps(str(self.laps_amount))
                    self.big_window.set_split_time(
                        str(f"{split_min:02d}:{split_sec}"))
                    self.big_window.laps_layout.addWidget(
                        self.big_window.split_time)
                    self.write_split_times_to_file(1, finish_min=split_min, finish_sec=split_sec)

    def stopwatch_split_time2(self):
        split_min, split_sec = divmod((time.time() - self.start_time), 60)
        split_min = int(split_min)
        split_sec = f"{split_sec:.2f}"
        if self.big_window_stopwatch_flag2:
            if self.laps_amount2 <= 1:
                self.laps_amount2 -= 1
                self.stop_stopwatch()

            else:
                self.laps_amount2 -= 1
                self.laps.setText(str(self.laps_amount2))
                if self.septimewindow2:
                    self.big_window2.set_laps(str(self.laps_amount2))
                    self.big_window2.set_split_time(
                        str(f"{split_min:02d}:{split_sec}"))
                    self.big_window2.laps_layout.addWidget(
                        self.big_window2.split_time)
                    self.write_split_times_to_file(2, finish_min=split_min, finish_sec=split_sec)

    def stop_stopwatch(self):
        finish_min, finish_sec = divmod((time.time() - self.start_time), 60)
        if not self.laps.text():
            self.stopwatch_flag = False
        if self.checkbox_laps.isChecked() and self.laps_amount < 1 and self.laps_amount2 < 1:
            self.stopwatch_flag = False
        finish_min = int(finish_min)
        finish_sec = "{:.2f}".format(finish_sec)
        self.big_timer.setText(str(f"{finish_min:02d}:{finish_sec:>5}"))

        if self.laps.text():
            if (
                self.septimewindow
                and self.big_window_stopwatch_flag1
                and self.laps_amount < 1
            ):
                self.big_window.split_time.setParent(None)
                self.big_window.set_timer_text(
                    str(f"{finish_min:02d}:{finish_sec:>5}"))
                self.big_window_stopwatch_flag1 = False
                self.big_window.set_laps("FINISH")
                self.write_split_times_to_file(
                    1, finish=True, finish_min=finish_min, finish_sec=finish_sec)
            if (
                self.septimewindow2
                and self.big_window_stopwatch_flag2
                and self.laps_amount2 < 1
            ):
                self.big_window2.split_time.setParent(None)
                self.big_window2.set_timer_text(
                    str(f"{finish_min:02d}:{finish_sec:>5}"))
                self.big_window_stopwatch_flag2 = False
                self.big_window2.set_laps("FINISH")
                self.write_split_times_to_file(
                    2, finish=True, finish_min=finish_min, finish_sec=finish_sec)
        else:
            if self.septimewindow:
                self.big_window.set_timer_text(
                    str(f"{finish_min:02d}:{finish_sec:>5}"))
            if self.septimewindow2:
                self.big_window2.set_timer_text(
                    str(f"{finish_min:02d}:{finish_sec:>5}"))

        self.set_cancel_button_text()


class LapsSeperateTimerWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super(LapsSeperateTimerWindow, self).__init__()

        user32 = ctypes.windll.user32
        self.width = user32.GetSystemMetrics(0)
        self.height = user32.GetSystemMetrics(1)

        self.pixel_ratio = QGuiApplication.primaryScreen().devicePixelRatio()

        self.setWindowTitle("Timer")
        self.setWindowIcon(QIcon('icon/t.png'))
        self.resize(self.width, self.height)
        self.x = self.geometry().height()
        self.y = self.geometry().width()
        print(self.geometry())

        self.laps_remaining = QLabel()
        self.laps_remaining.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPixelSize(self.x / 7 / self.pixel_ratio)
        font.setFamily("Arial")
        self.laps_remaining.setFont(font)
        self.laps_remaining.setStyleSheet("background-color: yellow")
        self.split_time = QLabel()
        font = QFont()
        font.setPixelSize(self.x / 20 / self.pixel_ratio)
        self.split_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.split_time.setFont(font)

        self.laps_layout = QVBoxLayout()
        self.laps_layout.addWidget(self.laps_remaining, 1)

        self.timer = QLabel()
        self.timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer.setObjectName("timer")
        font = QFont()
        font.setPixelSize(self.x / 6 / self.pixel_ratio)
        self.timer.setFont(font)
        # self.timer.setFont(QFont("Arial", self.x / 3))

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.laps_layout, 1)
        self.main_layout.addWidget(self.timer, 4)
        self.setLayout(self.main_layout)

    def closeEvent(self, event):
        self.closed.emit()
        # MainWindow.close_window(self)

    def set_split_time(self, str):
        self.split_time.setText("Split Time " + str)

    def finish_background_green(self):
        self.timer.setStyleSheet("background-color: green")

    def finish_background_reset(self):
        self.timer.setStyleSheet("")

    def set_laps(self, str):
        self.laps_remaining.setText("<h1>" + str + "</h1>")

    def set_timer_text(self, str):
        self.timer.setText("<h1>" + str + "</h1>")

    def set_font_size_to_stopwatch(self, multiplier=6):
        font = QFont()
        font.setPixelSize(self.x / multiplier / self.pixel_ratio)
        self.timer.setFont(font)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.close()
            # MainWindow.close_window(self)


class SeperateTimerWindow(LapsSeperateTimerWindow):
    def __init__(self):
        super().__init__()

        self.laps_remaining.setParent(None)
        self.laps_layout.setParent(None)

        self.set_font_size_to_stopwatch(multiplier=3)


class ConfigureUSBWindow(QDialog):
    def __init__(self, parent=None):
        super(ConfigureUSBWindow, self).__init__(parent)

        self.setObjectName("usbDialog")
        self.setWindowTitle("Select Arduino Device")
        self.resize(291, 276)
        self.setWindowIcon(QIcon('icon/t.png'))

        self.usbListButtonBox = QDialogButtonBox()
        self.usbListButtonBox.setOrientation(Qt.Orientation.Horizontal)
        self.usbListButtonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.usbListButtonBox.setObjectName("usbListButtonBox")
        self.usbList = QListWidget()
        self.usbList.setObjectName("usbList")

        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            self.usbList.addItem(p.description)

        # EVENTS
        self.usbListButtonBox.accepted.connect(self.accept)
        self.usbListButtonBox.accepted.connect(
            lambda: self.search_arduino_com_port(self.usbList.itemClicked))
        self.usbListButtonBox.rejected.connect(self.reject)

        # LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(self.usbList)
        layout.addWidget(self.usbListButtonBox)
        self.setLayout(layout)

    # FUNCTIONS
    def search_arduino_com_port(self, item):
        var = self.usbList.currentItem()
        if var != None:
            item_str = str(var.text())
            searchCOM = item_str.find("COM")
            MainWindow.set_arduino_port(
                self.parent(), item_str[searchCOM:searchCOM + 4])
        else:
            return None
