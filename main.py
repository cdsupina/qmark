from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QRadioButton, QScrollArea, QWidget, QButtonGroup
from PyQt5.QtGui import QFont
import sys


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
        self.question_count, self.output_file = self.init_result_file()
        #self.question_labels = [QLabel(self) for _ in range(self.question_count)]
        self.choice_count = 4
        self.question_label_x = 20
        self.question_label_y = 20
        self.question_offset = 100

        self.choices_x = 40
        self.choices_y = 60
        self.choice_spacing = 50
        self.choice_offset = 30

        self.questions = []

        self.init_ui()

    @staticmethod
    def init_result_file():
        assert len(sys.argv) == 3, ('Wrong number of arguments given. Specify an integer number of questions followed'
                                    'by an output file location.')

        with open(sys.argv[2], 'w') as output_file:
            for _ in range(int(sys.argv[1]) - 1):
                output_file.write('\n')

        return int(sys.argv[1]), sys.argv[2]

    def init_questions(self):
        result = []
        for q_num in range(self.question_count):
            label = QLabel(self.central_widget)
            label.setText('Question ' + str(q_num+1))
            label.move(self.question_label_x, self.question_label_y + (q_num * self.question_offset))
            label.setFont(QFont('Ariel', 15))

            choice_group = QButtonGroup(self.central_widget)
            choices = [QRadioButton(self.central_widget) for _ in range(self.choice_count)]

            for (i, choice) in enumerate(choices):
                choice.toggled.connect(self.select_answer)
                choice.move(self.choices_x + (i * self.choice_spacing), self.choices_y + (q_num * self.question_offset))
                choice.setText(chr(65+i))
                choice_group.addButton(choice)

            result.append(QMarkMultipleChoiceQuestion(label, choice_group, q_num))

        return result

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

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

    def select_answer(self):
        answer_button = self.sender()

        for question in self.questions:
            if answer_button in question.choices.buttons():
                with open(self.output_file) as output_file:
                    file_contents = output_file.readlines()

                file_contents[question.idx] = answer_button.text() + '\n'

                with open(self.output_file, 'w') as output_file:
                    output_file.writelines(file_contents)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())