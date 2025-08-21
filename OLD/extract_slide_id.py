from bs4 import BeautifulSoup

def extract_slide_id(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    icons = soup.find_all('i', class_='fa fa-youtube-play py-2 mx-2')
    
    slide_ids = []
    for icon in icons:
        li_element = icon.find_parent('li')
        if li_element:
            slide_id = li_element.get('data-slide-id')
            if slide_id:
                slide_ids.append(slide_id)
    
    return slide_ids

def get_slide_ids_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    return extract_slide_id(html_content)

if __name__ == "__main__":
    slide_ids = get_slide_ids_from_file('OLD/Lms.html')
