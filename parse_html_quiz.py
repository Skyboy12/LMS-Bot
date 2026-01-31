#!/usr/bin/env python3
"""
Script to parse HTML quiz files and extract quiz data for ADD_QUIZ_DATA command.
"""
import re
import json
from pathlib import Path

def parse_quiz_html(html_file_path):
    """
    Parse an HTML quiz file and extract:
    - slide_id
    - list of question_ids (in order)
    - correct answer_ids for each question
    """
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract slide ID from URL or data attribute
    slide_id_match = re.search(r'data-main-object="slide\.slide\((\d+),\)"', content)
    if not slide_id_match:
        slide_id_match = re.search(r'/slides/slide/[^/]+-(\d+)', content)
    
    if not slide_id_match:
        raise ValueError("Không tìm thấy slide ID trong file HTML")
    
    slide_id = int(slide_id_match.group(1))
    
    # Extract all questions with their data-question-id
    question_pattern = re.compile(
        r'<div[^>]+class="[^"]*o_wslides_js_lesson_quiz_question[^"]*"[^>]+data-question-id="(\d+)"',
        re.DOTALL
    )
    
    questions = question_pattern.findall(content)
    question_ids = [int(qid) for qid in questions]
    
    # For each question, find the correct answer
    # The correct answer has class "list-group-item-action" or contains fa-check-circle with text-success
    correct_answers = []
    
    # Split content by question divs
    question_blocks = re.split(
        r'<div[^>]+class="[^"]*o_wslides_js_lesson_quiz_question[^"]*"[^>]+data-question-id="\d+"',
        content
    )[1:]  # Skip the part before first question
    
    for i, block in enumerate(question_blocks):
        # Find the answer that has the success check icon
        # Look for pattern: data-answer-id="XXX" ... fa-check-circle text-success
        answer_pattern = re.compile(
            r'data-answer-id="(\d+)"[^>]*>.*?<i[^>]+class="[^"]*fa-check-circle[^"]*text-success[^"]*"',
            re.DOTALL
        )
        
        matches = answer_pattern.findall(block)
        if matches:
            correct_answers.append(int(matches[0]))
        else:
            # If no success icon found, look for list-group-item-action (active answer)
            answer_pattern_active = re.compile(
                r'data-answer-id="(\d+)"[^>]+class="[^"]*list-group-item-action[^"]*"',
                re.DOTALL
            )
            matches_active = answer_pattern_active.findall(block)
            if matches_active:
                correct_answers.append(int(matches_active[0]))
            else:
                # Default to first answer if cannot find correct one
                answer_any = re.search(r'data-answer-id="(\d+)"', block)
                if answer_any:
                    correct_answers.append(int(answer_any.group(1)))
                else:
                    correct_answers.append(0)
    
    if len(question_ids) != len(correct_answers):
        print(f"Warning: Found {len(question_ids)} questions but {len(correct_answers)} answers")
    
    return slide_id, question_ids, correct_answers

def generate_discord_command(slide_id, question_ids, correct_answers):
    """
    Generate Discord bot command for add_quiz.
    
    For each question, we need:
    - quiz_id: the question ID
    - start: the correct answer ID
    - amount: number of possible answers (default to 4 if unknown)
    """
    # Assume 4 possible answers per question (standard multiple choice)
    # This can be adjusted based on actual HTML parsing if needed
    amounts = [4] * len(question_ids)
    
    quiz_ids_str = ",".join(map(str, question_ids))
    starts_str = ",".join(map(str, correct_answers))
    amounts_str = ",".join(map(str, amounts))
    
    command = f"!add_quiz {slide_id} {quiz_ids_str} {starts_str} {amounts_str}"
    
    return command, {
        "slide_id": slide_id,
        "quiz_ids": question_ids,
        "starts": correct_answers,
        "amounts": amounts
    }

if __name__ == "__main__":
    # Parse the HTML file for quiz 3.1
    html_file = Path(r"d:\LMS - server\Triết Mác-LêNin\Câu hỏi Chương 3.1 _ PTIT.html")
    
    if not html_file.exists():
        print(f"File không tồn tại: {html_file}")
        exit(1)
    
    print(f"Đang phân tích file: {html_file.name}")
    print("-" * 60)
    
    try:
        slide_id, question_ids, correct_answers = parse_quiz_html(html_file)
        
        print(f"Slide ID: {slide_id}")
        print(f"Số câu hỏi: {len(question_ids)}")
        print()
        
        print("Chi tiết:")
        for i, (qid, ans) in enumerate(zip(question_ids, correct_answers), 1):
            print(f"  {i}. Question ID: {qid:4d} → Correct Answer ID: {ans}")
        
        print()
        print("-" * 60)
        
        command, data = generate_discord_command(slide_id, question_ids, correct_answers)
        
        print("Discord Command:")
        print(command)
        print()
        
        print("Hoặc dùng Python trực tiếp:")
        print(f"from send_packet import SEND_PACKET")
        print(f"SEND_PACKET.ADD_QUIZ_DATA({slide_id}, {question_ids}, {correct_answers}, {data['amounts']})")
        
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
