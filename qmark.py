from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QRadioButton, QScrollArea, QWidget, QButtonGroup, QCheckBox, QMessageBox, QPushButton
from PyQt5.QtGui import QFont, QIcon, QCloseEvent
from PyQt5.QtCore import Qt
import sys
import os


class QMarkMultipleChoiceQuestion():
    def __init__(self, label, choices, review, idx):
        self.label = label
        self.choices = choices
        self.review = review
        self.idx = idx


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'qmark'
        self.left = 50
        self.top = 50
        self.width = 400
        self.height = 520

        # create result file from command args
        self.question_count, self.output_file, self.starting_answers = self.init_result_file()
        self.choice_count = 5
        self.question_label_x = 20
        self.question_review_x = 150
        self.question_label_y = 20
        self.question_offset = 100

        self.choices_x = 40
        self.choices_y = 60
        self.choice_spacing = 50
        self.choice_offset = 30

        self.submit_button_x = 20
        self.submit_button_y_offset = 100
        self.credits_x = 20
        self.credits_y_offset = 150
        self.bottom_y = 130
        self.questions = []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.setWindowIcon(QIcon('qmark_logo.png'))
        self.central_widget = QWidget(self)

        scroll_length = 0
        if self.question_count > 5:
            scroll_length = ((self.question_count - 5) * self.question_offset) + self.bottom_y
        self.central_widget.setGeometry(0, 0, self.width - 100, self.height + scroll_length)

        self.submit = QPushButton('Submit and Exit', self.central_widget)
        self.submit.clicked.connect(self.close)
        self.credits = QLabel(self.central_widget)
        self.credits.setText('Written by Carlo Supina\nSubmit issues and PRs here:\nhttps://github.com/cdsupina/qmark')
        self.credits.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.questions = self.init_questions()

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(0, 0, self.width, self.height)
        self.scroll_area.setWidget(self.central_widget)

        self.show()

    def init_questions(self):
        result = []
        ypos = 0
        for q_num in range(self.question_count):
            if self.starting_answers:
                loaded_answer = self.starting_answers[q_num][0]
            label = QLabel(self.central_widget)
            label.setText('Question ' + str(q_num+1))
            ypos = self.question_label_y + (q_num * self.question_offset)
            label.move(self.question_label_x, ypos)
            label.setFont(QFont('Ariel', 15))
            if loaded_answer != '\n':
                label.setStyleSheet('background-color:#8affa3')
            else:
                label.setStyleSheet('background-color:#ff6262')

            review = QCheckBox(self.central_widget)
            review.setText('Review')
            review.move(self.question_review_x, ypos)
            review.toggled.connect(self.toggle_review)

            choice_group = QButtonGroup(self.central_widget)
            choices = [QRadioButton(self.central_widget) for _ in range(self.choice_count)]

            for (i, choice) in enumerate(choices):
                choice.toggled.connect(self.select_answer)
                choice.move(self.choices_x + (i * self.choice_spacing), self.choices_y + (q_num * self.question_offset))
                choice.setText(chr(65+i))

                if chr(65+i) == loaded_answer:
                    choice.setChecked(True)

                choice_group.addButton(choice)

            result.append(QMarkMultipleChoiceQuestion(label, choice_group, review, q_num))

        self.submit.move(self.submit_button_x, ypos + self.submit_button_y_offset)
        self.credits.move(self.credits_x, ypos + self.credits_y_offset)

        return result

    def select_answer(self):
        answer_button = self.sender()

        for question in self.questions:
            if answer_button in question.choices.buttons():
                with open(self.output_file) as output_file:
                    file_contents = output_file.readlines()

                # the following 3 lines fix '&' on first line quirk with linux
                text = answer_button.text() + '\n'
                while text.startswith('&'):
                    text = text[1:]
                file_contents[question.idx] = text

                with open(self.output_file, 'w') as output_file:
                    output_file.writelines(file_contents)

                question.label.setStyleSheet('background-color:#8affa3')

    def toggle_review(self):
        review_checkbox = self.sender()

        for question in self.questions:
            if review_checkbox is question.review:
                if review_checkbox.isChecked():
                    question.label.setStyleSheet('background-color:#f6ff89')
                else:
                    question.label.setStyleSheet('background-color:#ff6262')
                    for answer_button in question.choices.buttons():
                        if answer_button.isChecked():
                            question.label.setStyleSheet('background-color:#8affa3')

    @staticmethod
    def init_result_file():
        assert len(sys.argv) == 3, ('Wrong number of arguments given. Specify an integer number of questions followed'
                                    'by an output file location.')

        # if the output file already exists load the answers
        starting_answers = []
        if os.path.isfile(sys.argv[2]):
            with open(sys.argv[2]) as output_file:
                starting_answers = output_file.readlines()

            if len(starting_answers) < int(sys.argv[1]):
                print('Existing file ' + sys.argv[2] + ' contains fewer than ' + sys.argv[1]
                      + ' answers. Adding newlines(\'\\n\') to close the difference.')
                for _ in range(int(sys.argv[1]) - len(starting_answers)):
                    starting_answers.append('\n')
                with open(sys.argv[2], 'w') as output_file:
                    output_file.writelines(starting_answers)

            if len(starting_answers) > int(sys.argv[1]):
                print('Existing file ' + sys.argv[2] + ' contains greater than ' + sys.argv[1]
                      + ' answers. Removing lines to close the difference.')
                for _ in range(len(starting_answers) - int(sys.argv[1])):
                    starting_answers = starting_answers[:-1]
                with open(sys.argv[2], 'w') as output_file:
                    output_file.writelines(starting_answers)

        else:
            with open(sys.argv[2], 'w') as output_file:
                for _ in range(int(sys.argv[1])):
                    output_file.write('\n')

        return int(sys.argv[1]), sys.argv[2], starting_answers

    def closeEvent(self, event: QCloseEvent) -> None:
        # count unanswered quesitons and questions marked for review
        unanswered = ''
        with open(sys.argv[2]) as output_file:
            answers = output_file.readlines()
        for (i, answer) in enumerate(answers):
            if len(answer) == 1:
                unanswered += str(i+1) + ', '

        if len(unanswered) > 0:
            unanswered = unanswered[:-2]
        else:
            unanswered = 'None'

        marked_for_review = ''
        for question in self.questions:
            if question.review.isChecked():
                marked_for_review += str(question.idx + 1) + ', '
        if len(marked_for_review) > 0:
            marked_for_review = marked_for_review[:-2]
        else:
            marked_for_review = 'None'
        quit_msg = 'Exit Qmark?\nQuestions marked for review: ' + marked_for_review + '\nQuestions unanswered: ' + unanswered

        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())