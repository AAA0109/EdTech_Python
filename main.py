from datetime import datetime
from re import S
import pandas as pd
from numpy import random
import math

from classes import Answer
from classes import Question
from classes import QuestionTemplate
from classes import Response
from classes import HintResponse

def create_question_templates(df):
    ### loop through every row in the data frame, and create a question template
    
    list = []

    for r in df.index:
        qt = QuestionTemplate(df['index'][r],df['question_template_name'][r],df['group'][r]) # https://www.geeksforgeeks.org/different-ways-to-iterate-over-rows-in-pandas-dataframe/
        list.append(qt)

    return list

def print_question_templates(list):
    ### loop throug the list and print
    a = 0
    while a < len(list):
        print('id:' + str(list[a].id) + ',       Name:' + list[a].question_template_name + ',        Group:' + list[a].group)
        a = a + 1


def create_questions_answers(df,qt_list):
    ### loop through every row in the data frame, and create a question
    
    question_bank = {}
    id = 9001
    value = []
    answers = []

    for r in df.index:
        template = df['question_template_name'][r]
        q = Question(   id,
                        df['question_text_1'][r],
                        template,
                        df['difficulty'][r],
                        df['question_text_2'][r],
                        df['question_text_equation'][r]
                        )
        if template not in question_bank.keys():
            question_bank[template] = []
        question_bank[template].append(q)

        # fill in answers
        next_q_template_text = df['answer_1_next_q_template'][r]
        qt = search_q_template_list(qt_list,next_q_template_text)
        a1 = Answer(    df['answer_1_text'][r],
                        q,
                        df['answer_1_correct'][r],
                        df['answer_1_option'][r],
                        qt)
        answers.append(a1)
        
        next_q_template_text = df['answer_2_next_q_template'][r]
        qt = search_q_template_list(qt_list,next_q_template_text)
        a2 = Answer(    df['answer_2_text'][r],
                        q,
                        df['answer_2_correct'][r],
                        df['answer_2_option'][r],
                        qt)
        answers.append(a2)
        
        next_q_template_text = df['answer_3_next_q_template'][r]
        qt = search_q_template_list(qt_list,next_q_template_text)
        if len(str(df['answer_3_correct'][r])) > 0:
            a3 = Answer(    df['answer_3_text'][r],
                            q,
                            df['answer_3_correct'][r],
                            df['answer_3_option'][r],
                            qt)
            answers.append(a3)

        id = id + 1
    
    value.append(question_bank)
    value.append(answers)

    return value

def create_hints(hints_df):
    hints = {}

    for row in hints_df.index:
        gap = hints_df['gap'][row]

        hint = HintResponse(    hints_df['hint_question_text'][row],
                        hints_df['hint_answer_1_text'][row],
                        hints_df['hint_answer_2_text'][row],
                        hints_df['hint_answer_1_correct'][row],
                        hints_df['hint_answer_2_correct'][row],
                        hints_df['hint_answer_1_option'][row],
                        hints_df['hint_answer_2_option'][row]
                        )

        hints[gap] = hint

    return hints

def print_hints(hints):
    for hint in hints.values():
        print(hint.hint_question_text)
    return

def search_q_template_list(q_template_list, q_template_text):
    ### search the list of question templates, and return the question template that matches the text
    if q_template_text == 'exit':
        return 'exit'

    for qt in q_template_list:
        if qt.question_template_name == q_template_text:
            return qt
    return

def print_questions(question_bank, question_template_name):
    ### loop through the list for the current question template from the question_bank, and print it out
    lis = question_bank[question_template_name]
    for q in lis:
        print(q.question_text_1)

def create_module(df,qt_list):
    module = []
    for r in df.index:
        module.append(qt_list[df['index'][r]])
    return module

def print_responses(history):
    for response in history:
        print('Topic:' + str(response.qt.question_template_name) + ' ,' 
                + 'Question:' + str(response.question.question_text_1) + ' ,' 
                + 'Answer:' + str(response.answer.option) + ' ' + str(response.answer.answer_text) + ' ,'
                + 'correct:' + str(response.correct) + ' ,'
                + 'next topic:' + str(response.next_qt)
                )

def consecutive_correct(history,question_template):
    num = 0
    current_topic_responses = [r for r in history if r.qt == question_template]
    for response in current_topic_responses:
        if response.correct == True:
            num = num + 1
        else:
            num = 0
    
    return num

def consecutive_incorrect(history,question_template):
    num = 0
    current_topic_responses = [r for r in history if r.qt == question_template]
    for response in current_topic_responses:
        if response.correct == False:
            num = num + 1
        else:
            num = 0
    
    return num

def recent_correct(history,question_template):
    num = 0
    current_topic_responses = [r for r in history if r.qt == question_template]

    while len(current_topic_responses) > 5:
        current_topic_responses.pop(0)

    for response in current_topic_responses:
        if response.correct == True:
            num = num + 1
    return num

def recent_incorrect(history,question_template):
    num = 0
    current_topic_responses = [r for r in history if r.qt == question_template]

    while len(current_topic_responses) > 5:
        current_topic_responses.pop(0)

    for response in current_topic_responses:
        if response.correct == False:
            num = num + 1
    return num


def hint_heuristic_1(history, question_template):
    ## hint heuristic #1
        ## description
            ## pass in the history and a question template, and find out if the question is one of 2 incorrect in a visit
        ## return value
            ## true if the heuristic is met, false if not
        ## assumptions
            ## this heuristic is called regardless of whether the question is correct/incorrect

    ## if this is the first question ever, return false
    if len(history) == 0: 
        print('hint_heuristic_1:False') 
        return False
    ## if the most recent question in history is correct, then return false
    elif history[len(history)-1].correct == True: 
        print('hint_heuristic_1:False') 
        return False

    ## define constants
    filtered_history_this_visit = []
    num_incorrect = 0
    threshold = 2

    index = len(history) - 1
    while index >= 0:
        if history[index].qt != question_template: break
        filtered_history_this_visit.insert(0,history[index])
        index = index - 1

    if len(filtered_history_this_visit) == 0: 
        print('hint_heuristic_1:False') 
        return False

    for h in filtered_history_this_visit:
        if h.correct == False:
            num_incorrect = num_incorrect + 1

    print('hint_heuristic_1:False') if num_incorrect > threshold else print('hint_heuristic_1:True')
    return False if num_incorrect > threshold else True


def hint_heuristic_2(history, question_template):
    ## hint heuristic #2
        ## description
            ## pass in the history and a question template, and show a hint for the first 2 high difficulty incorrect answers in the visit
        ## return value
            ## true if the heuristic is met, false if not
        ## assumptions
            ## this heuristic is called regardless of whether the question is correct/incorrect

    ## define constants
    filtered_history_this_visit = []
    num_incorrect = 0
    threshold = 2
    difficulty = 'high'

    ## if this is the first question ever, return false
    if len(history) == 0: 
        print('hint_heuristic_2:False') 
        return False
    
    last_element = history[len(history)-1]
    ## if the most recent question in history is correct, or it's not high difficulty, then return false
    if last_element.correct == True or last_element.question.difficulty != difficulty: 
        print('hint_heuristic_2:False') 
        return False

    index = len(history) - 1
    while index >= 0:
        if history[index].qt != question_template: break
        filtered_history_this_visit.insert(0,history[index])
        index = index - 1

    if len(filtered_history_this_visit) == 0:
        print('hint_heuristic_2:False') 
        return False

    for h in filtered_history_this_visit:
        if h.correct == False and h.question.difficulty == difficulty:
            num_incorrect = num_incorrect + 1

    print('hint_heuristic_2:False') if num_incorrect > threshold else print('hint_heuristic_2:True')
    return False if num_incorrect > threshold else True

def hint_heuristic_3(history, question_template):
    ## hint heuristic #3
        ## description
            ## pass in the history and question template, and show a hint if there have been 2 questions wrong in a row, disregardinf visit
        ## return value
            ## true if the heuristic is met, false if not
        ## assumptions
            ## this heuristic is called regardless of whether the question is correct/incorrect

    if len(history) < 2:
        print('hint_heuristic_3:False') 
        return False
    
    last1_element = history[len(history)-1]
    last2_element = history[len(history)-2]
    if last1_element.correct == False:
        if last2_element.correct == False:
            print('hint_heuristic_3:True') 
            return True
    
    print('hint_heuristic_3:False') 
    return False

def hint_heuristic_4(history, question_template):
    ## hint heuristic #4
        ## description
            ## pass in the history and question template, and show a hint if there have been 2 questions of med or high difficulty incorrect in a row (not consecutive)
            ## for the current visit
        ## return value
            ## true if the heuristic is met, false if not
        ## assumptions
            ## this heuristic is called regardless of whether the question is correct/incorrect

    ## define constants
    excluded_difficulty = 'low'
    filtered_history_this_visit = []

    ## if this is the first question ever, return false
    if len(history) == 0: 
        print('hint_heuristic_4:False') 
        return False
    
    last_element = history[len(history)-1]
    ## if the most recent question in history is correct or low difficulty then return false
    if last_element.correct == True or last_element.question.difficulty == excluded_difficulty:
        print('hint_heuristic_4:False') 
        return False

    ## get the filtered history for this visit only
    index = len(history) - 1
    while index >= 0:
        if history[index].qt != question_template: break
        filtered_history_this_visit.insert(0,history[index])
        index = index - 1

    ## if the filtered history for this visit is less than 2 elements, then this heuristic cannot be true
    if len(filtered_history_this_visit) < 2:
        print('hint_heuristic_4:False')
        return False

    ## at this point, we know that the last element is high or med difficulty, and incorrect
    ## so we want to find the last same difficulty (med or high) and if it was incorrect, return True
    last_element = filtered_history_this_visit[len(filtered_history_this_visit)-1]
    index = len(filtered_history_this_visit) - 2
    while index >= 0:
        compare_element = filtered_history_this_visit[index]
        if compare_element.question.difficulty == last_element.question.difficulty and compare_element.correct == False:
            print('hint_heuristic_4:True') 
            return True
        index = index - 1

    print('hint_heuristic_4:False')
    return False

def vid_heuristic_1():
    return

def vid_heuristic_2():
    return

def vid_heuristic_3():
    return

def up_heuristic_1(history,question_template):
    ## move up heuristic #1
        ## description
            ## pass in the history, a question template, and a difficulty level & figure out how many of the last 5 of a certain difficulty are correct 
        ## rule
            ## the child has answered 4 out of the last 5 high difficulty questions correctly
        ## return value
            ## true if the heuristic is met, false if not

    ## define the constants
    difficulty = 'high'
    threshold = 4
    num_to_check = 5

    ## filter the history for these question templates only, and this question difficulty only
    filtered_history = [r for r in history if r.qt == question_template]
    filtered_history_q_difficulty = [h for h in history if h.qt == question_template and h.question.difficulty == difficulty]

    ## if they haven't even answered 5 for this question template then this heuristic does not apply
    if len(filtered_history) < 5:
        print('up_heuristic_1:False')
        return False

    ## truncate to take only the last 5 entries in the filtered history for this question difficulty
    num = min(num_to_check,len(filtered_history_q_difficulty))
    last5 = filtered_history_q_difficulty[len(filtered_history_q_difficulty)-num:] 

    ## loop through and count how many of the last 5 they got correct
    num_correct = 0
    for h in last5:
        if h.correct == True:
            num_correct = num_correct + 1
    print('up_heuristic_1:True') if num_correct >= threshold else print('up_heuristic_1:False')
    return True if num_correct >= threshold else False

def down_heuristic_1(history, question_template):
    ## move down heuristic #1
        ## description
            ## the child has seen too many questions since the last high difficulty one for the current visit to the node.
            ## Since the question difficulty tends towards getting more difficult, this indicates that the child is struggling.
        ## rule
            ## In any question template (concept area), if the child answers 8 questions in a row of the same question template 
            ## without coming to a high difficulty question, then move them down
    ## return values
        ## true if the heuristic is met, false if not

    ## define the constants
    num_to_check = 8
    difficulty = 'high'
    filtered_history_this_visit = []

    if len(history) == 0: return False
    ## if they haven't answered 8 questions total, this heuristic does not apply
    elif len(history) < num_to_check:
        print('down_heuristic_1:False')
        return False
    
    ## filter the history for only the history from the last 
    ## does this work right when you come off of a node? essentially when filtered_history_this_visit would be empty? I guess in theory it should hit
    ## the if statement because the current question template will not match.
    index = len(history) - 1
    while index >= 0:
        if history[index].qt != question_template: break
        filtered_history_this_visit.insert(0,history[index])
        index = index - 1
    
    ## if they haven't even answered 8 questions for this question template, this heuristic does not apply
    if len(filtered_history_this_visit) < num_to_check:
        print('down_heuristic_1:False')
        return False

    ## truncate to take only the last 8 entries in the filtered_history 
    num = min(num_to_check,len(filtered_history_this_visit))
    last8 = filtered_history_this_visit[len(filtered_history_this_visit)-num:] 

    ## assume that the last 8 are not high difficulty. Falsify this assumption if:
        # last 8 are not in the same question template, so the kid has moved on -> return False
        # one of the last8 is high difficulty -> return False
    
    for l in last8:
        ## if one of the last 8 in this question template is a high difficulty question
        if l.question.difficulty == difficulty: 
            print('down_heuristic_1:False')
            return False

    print('down_heuristic_1:True')
    return True

def down_heuristic_2(history, question_template):
    """
        Potential issues:
            you did not filter the history for the current question template, so it will be mixing questions from other question templates
    """
     
     ## move down heuristic #2
        ## description
            ## the child has gotten 3 low difficulty incorrect in a row, so they should definitely move down
        ## rule
            ## In any question template (concept area), if the child answers 3 low difficulty questions in a row incorrect, then move down
            ## notable: you need to check the use case when they are re-visiting the node from before. This does not remove the history that the child from the first visit.
    ## return values
        ## true if the heuristic is met, false if not

    ## define the constants
    num_to_check = 3
    difficulty = 'low'

    # if they haven't even answered 3 questions this heuristic does not apply
    if len(history) < num_to_check:
        print('down_heuristic_2:False')
        return False

    ## truncate to take only the last 3 entries to history
    last3 = history[len(history)-num_to_check:] 

    ## assume that the last 3 history are low difficulty incorrect. Falsify this assumption if any of the conditions are met:
    for l in last3:
        ## if one of the last 3 is correct:
        if l.correct == True and l.question.difficulty == difficulty: 
            print('down_heuristic_2:False')
            return False

        ## if one of the last 3 is not low difficulty:
        if l.question.difficulty != difficulty:
            print('down_heuristic_2:False')
            return False

        ## if one of the last 3 is not in the question template
        if l.qt != question_template:
            print('down_heuristic_2:False')
            return False
    
    print('down_heuristic_2:True')
    return True

def down_heuristic_3(history, question_template):
    ## move down heuristic #3
        ## description
            ## the child has gotten 3 of the last 5 low difficulty in a particular question template incorrect, so move them down 
            ## we filter out previous visits and just look at the current visit
        ## rule
            ## In any question template (concept area), if the child has answered 3 of the last 5 low difficulty 
            ## questions incorrect, then move them down
    ## return values
        ## true if the heuristic is met, false if not
    
    ## define the constants
    num_to_check = 5
    difficulty = 'low'
    threshold = 3
    filtered_history_this_visit = []

    if len(history) > 20:
        print('hi')
    
    ## only consider the history of the same question template and question difficulty
    ## disgregard previous visits of the node by breaking the loop if a response in the history has a different qt
        ## this algo rests on the assumption that you can identify that this is a secondary visit by seeing consecutive responses with different qt. 
            ## the first qt will be of the current question template
            ## the second qt will be of the previous question template whether parent or child
    index = len(history) - 1
    while index >= 0:
        if history[index].qt != question_template: break 
        filtered_history_this_visit.insert(0,history[index])
        index = index-1

    ## truncate to take only the low difficulty questions for this visit
    last5 = [r for r in filtered_history_this_visit if r.question.difficulty == difficulty]

    ## if they haven't even answered 5 low difficulty questions in this template, for this visit this heuristic does not apply
    if len(last5) < num_to_check:
        print('down_heuristic_3:False')
        return False

    ## take only the last 5 low difficulty questions for this visit that were answered
    last5 = last5[len(last5)-num_to_check:]

    ## loop through and count how many of the last 5 low difficulty they got incorrect
    num_incorrect = 0
    for l in last5:
        if l.correct == False and l.question.difficulty == difficulty:
            num_incorrect = num_incorrect + 1
    
    print('down_heuristic_3:True') if num_incorrect >= threshold else print('down_heuristic_3:False')
    return True if num_incorrect >= threshold else False

def down_heuristic_4(history, question_template):
    ## move down heuristic #4
        ## description
            ## the child has gotten 3 of the last 5 high difficulty in a particular question template incorrect, so move them down 
            ## we filter out previous visits and just look at the current visit. Non consecutive. 
        ## rule
            ## In any question template (concept area), if the child has answered 3 of the last 5 high difficulty 
            ## questions incorrect, then move them down. non consecutive.
    ## return values
        ## true if the heuristic is met, false if not
    
    ## define the constants
    num_to_check = 5
    difficulty = 'high'
    threshold = 3
    filtered_history_this_visit = []

    ## get the filtered history for this visit only
    index = len(history) - 1
    while index >= 0:
        if history[index].qt != question_template: break 
        filtered_history_this_visit.insert(0,history[index])
        index = index-1

    ## truncate to take only the high difficulty questions for this visit
    last5 = [r for r in filtered_history_this_visit if r.question.difficulty == difficulty]

    ## if they haven't even answered 5 high difficulty questions in this template, for this visit this heuristic does not apply
    if len(last5) < num_to_check:
        print('down_heuristic_3:False')
        return False

    ## take only the last 5 high difficulty questions for this visit that were answered
    last5 = last5[len(last5)-num_to_check:]

    ## loop through and count how many of the last 5 high difficulty they got incorrect
    num_incorrect = 0
    for l in last5:
        if l.correct == False and l.question.difficulty == difficulty:
            num_incorrect = num_incorrect + 1
    
    print('down_heuristic_5:True') if num_incorrect >= threshold else print('down_heuristic_5:False')
    return True if num_incorrect >= threshold else False

def down_heuristic_5(history, question_template):
    ## move down heuristic #5
        ## description
            ## the child has seen 5 total hints in a single visit, so move them down

    
    return

def move_up(history,question_template):
    ## this function returns true if 4 of the last 5 high difficulty questions for a particular question_template were answered correctly
    move_up_bool_list = []
    move_up_bool_list.append(up_heuristic_1(history,question_template))

    for u in move_up_bool_list:
        if u == True: return True

    return False

def move_down(history, question_template):
    # function to move down to a pre-requisite if the kid has mastered the topic, depending on the heuristic rules that we define

    ## this function returns true if there are several heuristics that are achieved that indicate that the child should move to a prerequisite topic
        ## notably, this function just returns true or false. To figure out which prerequisite to move down to is another function

    move_down_bool_list = []
    move_down_bool_list.append(down_heuristic_1(history,question_template))
    move_down_bool_list.append(down_heuristic_2(history,question_template))
    move_down_bool_list.append(down_heuristic_3(history,question_template))
    move_down_bool_list.append(down_heuristic_4(history,question_template))
    move_down_bool_list.append(down_heuristic_5(history,question_template))

    for b in move_down_bool_list:
        if b == True: return True
    
    return False

def find_prerequisite(current_question_template, q_template_list): ### 
    # if we are moving down, then we need to consider the history to determine which prerequisite to move into
    ## so in an arbitrary way, we should determine which prereq to move down into based on the history of responses
        ## method 1: we create a graph and determine which of the children to go into 
        ## method 2: we hardcode the logic into this function. So based on the current question template, we pick one of the question templates to go into

    ## this function also needs to figure out if we should "exit" because we have gotten to the bound. Maybe it returns false if that is the case.

    #if current_question_template.question_template_name == 'equations as constraints':

    return q_template_list[8]

def show_hint_bool(history, question_template):
    l = []
    l.append(hint_heuristic_1(history,question_template))
    l.append(hint_heuristic_2(history,question_template))
    l.append(hint_heuristic_3(history,question_template))
    l.append(hint_heuristic_4(history,question_template))

    for b in l:
        if b == True: 
            return True
    
    return False

def show_hint(hints, gap):
    print()
    hint = hints[gap]
    print('     ' + str(hint.hint_question_text))
    print('         ' + str(hint.hint_answer_1_text))
    print('         ' + str(hint.hint_answer_2_text))
    print()
    return input()

def show_video_bool(): ###
    return False

def show_video(): ###
    print('             *********this is a video*********')
    return

def translate_difficulty_to_score(difficulty):
    if difficulty == 'high': return 3
    elif difficulty == 'medium': return 2
    elif difficulty == 'low': return 1

def translate_score_to_difficulty(score):
    if score == 1: return 'low'
    elif score == 2: return 'medium'
    elif score == 3: return 'high'

def calculate_score(last2):
    ### last2 is a list of the last 2 Response objects for the current question template

    ## if the history has no responses, then it is a new node, start at medium score = 2
    if (len(last2) == 0):
        score = 2
    ## if the history has 1 response, then calculate the new score from the one score
    elif len(last2) == 1:
        score = translate_difficulty_to_score(last2[0].question.difficulty) if last2[0].correct == True else 0
        score = math.ceil(score + 0.5)
    ## otherwise, calculate the score from the last 2 scores
    elif len(last2) == 2:
        r1 = last2[0]
        r2 = last2[1]
        score1 = translate_difficulty_to_score(r1.question.difficulty) if r1.correct == True else 0 
        score2 = translate_difficulty_to_score(r2.question.difficulty) if r2.correct == True else 0
        score = (score1 + score2) / 2
        score = math.ceil(score + 0.5)

        #score = int(round(((score1 + score2) / 2) + 0.5)) ## are we sure that adding score1 and score2 produces a float?
        if score > 3:
            score = 3
    else:
        print('error')
        exit()
    print('score:' + str(score))
    return score

def choose_question(question_list, question_template, history):
    ## question_list is a list of Question objects which have question template = to the current question template
    ## question_template is the current Question Template object
    ## visited is a set that keeps track of whether a node was visited anytime in the last 100 iterations
    difficulty_score = 0
    last2 = []
    
    ## the question difficulty is selected based on the score

    ## find the history of respones on this question template
    temp_history_on_current_qt = [r for r in history if r.qt == question_template]
    ## if 2 questions have not been answered, then don't truncate the history
    if (len(temp_history_on_current_qt) < 2):
        last2 = temp_history_on_current_qt
    ## if more than 2 questions have been answered, then truncate to just get the last 2 responses
    else:  
        last2.append(temp_history_on_current_qt[-2])
        last2.append(temp_history_on_current_qt[-1])

    ## calculate the score by calling the function with the truncated history
    difficulty_score = calculate_score(last2)
    ## make a temporary list of questions from the question list passed in that match the difficulty and pick a random one
    temp_q_list = [q for q in question_list if q.difficulty == translate_score_to_difficulty(difficulty_score)] ## length of this should be 2 for now
    num = random.randint(len(temp_q_list))

    return temp_q_list[num] ## this resolves to a Question object

def ask_questions_interactive(q_template_list, question_template, question_bank, answers, history, input_list,hints):

    ## move down
        ## approach 1: use recursion (this approach doesn't let you move horizontally between prereq nodes, you can only move back up to the current child's parent node)
        ## approach 2: use a stack data structure to keep track of question templates to visit (this approach allows you to move horizontally between prereq nodes)

    ## move up
        ## if approach 1 move down implemented: just end the current loop and go back to the main function call to loop through for loop
            ## use case 1: current node is a parent "new" node -> you will go to the next "new" node
            ## use case 2: current node is a child "foundational" node
                ## if you implemented approach 1 for move down, you will go back up to the parent "new" node b/c recursive
        ## if approach 2 move down implemented: this one is a little trickier. You need to keep track of what node to visit next & probably not just rely on the for loop

    ## there are three exits to this function. Otherwise, you just keep seeing more questions
        ## exit 1: you master the current question template, and so you return from the move_up check to the main function call which exits this function call
        ## exit 2: you go outside the knowledge graph and need to speak with a tutor and the program quits
        ## semi exit 3: you return from move_down true which makes a recursive call to this function again:
            ## recursive stack: you are now in a child node & answering questions for that child node until once again exit 1, 2 or 3 is achieved
            ## if you master the child node and you "move up", then it returns and you come back to the original stack
            ## original stack: when you come back to the original stack, you continue with the loop again until once again exit 1, 2 or 3 is achieved

    while True:
        ## ask a question
        selected_question = choose_question(question_bank[question_template.question_template_name],question_template,history)

        ## display question and answer information to the user
        print('You are currently on the topic: ' + question_template.question_template_name)
        print('     ' + selected_question.question_text_1)
        selected_question_answer_options = [a for a in answers if a.question == selected_question]
        options = {}
        for a in selected_question_answer_options:
            options[a.option] = a
            print('            ' + a.answer_text)

        ## take input from the user
        if len(input_list) > 0:
            user_input = input_list.pop(0)
            print(user_input)
        else:
            user_input = input()

        ## continue asking questions as long as the user does not enter 'exit'
        if user_input == 'exit': quit()

        ## record the user's answer:
        selected_answer = options[user_input]
        history.append(Response(selected_question,question_template,selected_answer,selected_answer.correct,selected_answer.next_question_template))
        print()

        ## depending on the response, figure out if we should show hint and/or video
        if show_hint_bool(history,question_template): 
            user_input = show_hint(hints,q_template_list[8].question_template_name)
            ## what am I going to do based on the answer?
                ## I need to record the history of the hint (add it to hint list, and/or add it to history)
                ## I need to adjust the score
                ## I need to 
        if show_video_bool(): show_video()

        ## depending on the response, figure out the control flow for what template to show the kid next from the options: move up, move down, exit
        # use case 1: move up -> just return b/c we will go back to the main for loop & to the next template in the module list
        if move_up(history,question_template) == True: return
            ## one thing additional to do in the move up and move down, for now, you will need to clear hints
        
        ## use case 2: move down -> figure out which prereq template to go to and recurse on that question template
        if move_down(history,question_template) == True:
            prereq_qt = find_prerequisite(question_template,q_template_list) ## this function will return the prereq question template if there is one, or false if "exit"
            ## use case 3: exit -> there are no more prerequisites to explore in our limited knowledge graph
            if prereq_qt == False:
                print('speak with a tutor')
                print()
                quit()
            ask_questions_interactive(q_template_list,prereq_qt,question_bank,answers,history, input_list,hints) 

if __name__ == "__main__":

    ### create question_templates from the csv
    question_templates_df = pd.read_csv('question_templates.csv') # https://www.w3schools.com/python/pandas/pandas_csv.asp
    q_template_list = create_question_templates(question_templates_df) # it's important that this is an ordered list, because we will be accessing the order using the index

    ### create the questions & answers from the csv
    questions_df = pd.read_csv('questions.csv')
    q_and_a = create_questions_answers(questions_df,q_template_list)
    question_bank = q_and_a[0]
    answers = q_and_a[1]

    ### create the hints from the csv
    hints_df = pd.read_csv('hints.csv')
    hints = create_hints(hints_df) 

    ### create the module
    module_df = pd.read_csv('module.csv')
    module = create_module(module_df,q_template_list)

    history = []
    hint_history = [] ## at some point, might want to combine history and hint history

    input_list = []
    #input_list = list(('B','B','B','B','A','B','B','B','B','A','A','A','A','B','B','B','B','A','A','A','A','A','A','B','B','C','B','B','B'))

    ### loop through concepts & go down rabbit hole when necessary
    for m in module:
        ask_questions_interactive(q_template_list,m,question_bank,answers,history,input_list,hints)
    
    print('you are done with the unit, congrats')
    
