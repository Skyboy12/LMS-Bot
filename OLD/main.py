import time
import set_completed
import quiz
from importlib import reload

def main():
    quiz.submit_quiz() 
    time.sleep(0.5)
    set_completed.use_existing_session()   



if __name__ == "__main__":
    with open('SESSION_ID.txt', 'r') as f:
        for session_id in f.readlines():
            enviroment = open('.env','w')
            enviroment.write(f'SESSION_ID={session_id.strip()}')
            enviroment.close()
            set_completed = reload(set_completed)
            quiz = reload(quiz)
            main()
        f.close()
