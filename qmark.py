from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QRadioButton, QScrollArea, QWidget, QButtonGroup, QLayout
from PyQt5.QtGui import QFont, QIcon
import sys
import os


class QMarkMultipleChoiceQuestion():
    def __init__(self, label, choices, idx):
        self.label = label
        self.choices = choices
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
        self.question_label_y = 20
        self.question_offset = 100

        self.choices_x = 40
        self.choices_y = 60
        self.choice_spacing = 50
        self.choice_offset = 30

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
            scroll_length = (self.question_count - 5) * self.question_offset

        self.central_widget.setGeometry(0, 0, self.width - 100, self.height + scroll_length)
        self.questions = self.init_questions()

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(0, 0, self.width, self.height)
        self.scroll_area.setWidget(self.central_widget)

        self.show()

    def init_questions(self):
        result = []
        for q_num in range(self.question_count):
            loaded_answer = self.starting_answers[q_num][0]
            label = QLabel(self.central_widget)
            label.setText('Question ' + str(q_num+1))
            label.move(self.question_label_x, self.question_label_y + (q_num * self.question_offset))
            label.setFont(QFont('Ariel', 15))
            if loaded_answer != '\n':
                label.setStyleSheet('background-color:#8affa3')
            else:
                label.setStyleSheet('background-color:#ff6262')

            choice_group = QButtonGroup(self.central_widget)
            choices = [QRadioButton(self.central_widget) for _ in range(self.choice_count)]

            for (i, choice) in enumerate(choices):
                choice.toggled.connect(self.select_answer)
                choice.move(self.choices_x + (i * self.choice_spacing), self.choices_y + (q_num * self.question_offset))
                choice.setText(chr(65+i))

                if chr(65+i) == loaded_answer:
                    choice.setChecked(True)

                choice_group.addButton(choice)

            result.append(QMarkMultipleChoiceQuestion(label, choice_group, q_num))

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())