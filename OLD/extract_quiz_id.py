from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

def extract_quiz_id(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    icons = soup.find_all('i', class_='fa fa-question-circle-o py-2 mx-2')
    
    quiz_ids = []
    for icon in icons:
        li_element = icon.find_parent('li')
        if li_element:
            quiz_id = li_element.get('data-slide-id')
            if quiz_id:
                quiz_ids.append(quiz_id)
    
    return quiz_ids

def get_quiz_ids_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()  # Read the content of the file
    return extract_quiz_id(html_content)  # Pass the content to the function

if __name__ == "__main__":
    quiz_ids = get_quiz_ids_from_file('OLD/Lms.html')
    for quiz_id in quiz_ids:
        print(f"Found data-quiz-id: {quiz_id}")
