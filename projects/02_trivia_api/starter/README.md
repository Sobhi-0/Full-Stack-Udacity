# Full Stack API Final Project


## Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

In the application you can:

1. Display questions - both all questions and by category. Questions show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions.
4. Search for questions.
5. Play the quiz game, randomizing either all questions or within a specific category.

We are always working on enchancing the users' experience and we are always welcoming your improvments.

## Want to fix a bug? Or perhaps, add a feature?

If you are intrested in contributing into improving our application then kindly read the following:
- Follow the PEP8 style guide
- Our API follows the RESTFull principles

## Dependancies

-NodeJS 13.6.0

-Python 3

To install the ```requirements``` , in the backend dierectory run ```pip install -r requirements.txt```

### Backend

In the backend dierectory

bash:
```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```
===================================

PowerShell:
```PS
$env:FLASK_APP="flaskr"
$env:FLASK_DEBUG="true"
flask run
```

### Frontend

In the frontend dierectory ```npm install``` after installed ```npm start```

## API Documentation

### Getting Started
Base URL :  https://localhost:5000/

### Error Handling
We are using HTTP response codes to indicate the success or failure of an API request. The responses are formated in JSON indicating that a failure happend and showing the error code and message.

Example:

```JSON
{
    'success': False,
    'error_code': 404,
    'message': 'resource not found'
}
```

Errors that might be returned:
-400: Bad Request
-404: Resource Not Found
-422: Not Processable

### Endpoint Library

GET /categories
-
Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of {'id': 'category'}

Request URL example:

```bash
curl http://127.0.0.1:5000/categories
```

Response Example:

```JSON
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true
}
```

GET /questions
-
The response indicates the succes of the request and retreaves a list of all questions paginated and limited to 10 questions per page.
- Request Arguments: (optional) ```/?page=<page_number>```
- Returns: List of all categories and maximum 10 questions each question with id, answer, category_id, difficulty
Total number of questions
Current Category

Request URL example:

```bash
curl http://127.0.0.1:5000/questions?page=1
```

Response Example:

```JSON
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "questions": [
      {
          "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    }
  ]
  "success": true,
  "total_questions": 19,
  "current_category": 1
}
```

DELETE /questions/<question_id>
-
Deletes the question of the given ID if exists.
- Request Arguments: ```/<question_id>```
- Returns: ID of the deleted question with the total number of remaining questions

Request URL example:

```bash
curl -X DELETE http://127.0.0.1:5000/questions/5
```

Response Example:

```JSON
{
  "deleted": "5",
  "success": true,
  "total_questions": 18
}
```

POST /questions  (Add Question)
-
- Request Arguments: Question, Answer, Difficulty, Category
- Returns: The added question id and the total number of questions(including the new question)


Request URL example:

```bash
 curl -X POST -H "Content-Type: application/json" -d '{"question": "What is the capital of France?", "answer": "Paris", "difficulty": 2, "category": 3}' http://localhost:5000/questions
 ```

Response Example:

```JSON
{
  "created": 24,
  "success": true,
  "total_questions": 19
}
```

POST /questions  (Search for a Question)
-
- Request Arguments: Search term
- Returns: The number of questions found and the questions

Request URL example:

```bash
 curl -X POST -H "Content-Type: application/json" -d '{\"searchTerm\":\"title\"}' http://localhost:5000/questions
 ```

Response Example:

```JSON
{
  "found_questions": 1,
  "questions": [
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ],
  "success": true
}
```

GET /categories/<category_id>/questions
-
Gets questions by category
- Request Arguments: The category ID
- Returns: Current category, the number of the found questions and the questions

Request URL example:

```bash
curl http://127.0.0.1:5000/categories/5/questions
```

Response Example:

```JSON
{
  "current_category": "5",
  "questions": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

## Authors
- Team of Udacity
- Myself
