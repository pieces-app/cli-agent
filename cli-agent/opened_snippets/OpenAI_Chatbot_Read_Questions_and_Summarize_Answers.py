from openai import OpenAI
from dotenv import load_dotenv
def call_open_ai(questions, answers):
    load_dotenv()
    client = OpenAI()
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Read the ##QUESTIONS. Then summarize the ##ANSWERS and Return json with the keys 'Answer_1' 'Answer_2' 'Answer_3' 'Answer_4' 'Answer_5' 'Answer_6' 'Answer_7'"},
        {"role": "user", "content": f"##QUESTIONS: {questions}/n/n ##ANSWERS: {answers}"},
    ]
    )
    # content = response.choices[0].message.content
    # print(content)
    print(response.choices[0].message.content)
def read_and_print_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
            # print(contents)
            return contents
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
def main():
    # Replace 'your_file.txt' with the path to the text file you want to read.
    file_path_questions = 'questions.txt'
    file_path_answers = 
    questions = read_and_print_file(file_path_questions)
    answers = read_and_print_file(file_path_answers)
    response = call_open_ai(questions, answers)
    print(response)
if __name__ == "__main__":
    main()
