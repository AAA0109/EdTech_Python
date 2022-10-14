from datetime import datetime

class Answer:
    def __init__(self,text,question, correct,option, next_question_template=None):
        self.answer_text = text
        self.question = question
        self.correct = correct
        self.option = option
        self.next_question_template = next_question_template

class Question:
    def __init__(self, id, question_text_1, question_template, difficulty, question_text_2='', question_text_equation=''):
        # assigned automatically: question ID
        self.id = id
        self.question_text_1 = question_text_1
        self.question_template = question_template
        self.difficulty = difficulty
        self.question_text_2 = question_text_2
        self.question_text_equation = question_text_equation
        self.created_time = datetime.now()

class QuestionTemplate:
    def __init__(self, index, name, group):
        self.index = index
        self.question_template_name = name
        self.group = group
        self.children = []

    def add_child(self,child):
        self.children.append(child)

class Response:
    def __init__(self,Question,QuestionTemplate,Answer,correct,next_question_template):
        self.question = Question
        self.qt = QuestionTemplate
        self.answer = Answer
        self.correct = correct
        self.next_qt = next_question_template

# class History:
#     def __init__(self,type)

#         self.created_time = datetime.now()


class HintResponse:
    def __init__(self,hint_question_text,hint_answer_1_text,hint_answer_2_text,correct1,correct2,option1,option2):
        self.hint_question_text = hint_question_text
        self.hint_answer_1_text = hint_answer_1_text
        self.hint_answer_2_text = hint_answer_2_text
        self.hint_answer_1_correct = correct1
        self.hint_answer_2_correct = correct2
        self.hint_answer_1_option = option1
        self.hint_answer_2_option = option2

#class Video: ##??



    ## you might need to add hint objects to either response or make a new class

## next steps:
    ## figure out how to structure hints
    ## create hints csv & read into the program
    ## code the prereqs function
    ## adjust the score based on the hint
    ## figure out how to structure videos
    ## create videos csv & read into the program