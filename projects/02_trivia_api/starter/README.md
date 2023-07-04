# Full Stack API Final Project


## Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

That's where you come in! Help them finish the trivia app so they can start holding trivia and seeing who's the most knowledgeable of the bunch. The application must:

1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

Completing this trivia app will give you the ability to structure plan, implement, and test an API - skills essential for enabling your future applications to communicate with others.

## Starting and Submitting the Project

[Fork](https://help.github.com/en/articles/fork-a-repo) the [project repository](https://github.com/udacity/FSND/blob/master/projects/02_trivia_api/starter) and [Clone](https://help.github.com/en/articles/cloning-a-repository) your forked repository to your machine. Work on the project locally and make sure to push all your changes to the remote repository before submitting the link to your repository in the Classroom.
>Once you're ready, you can submit your project on the last page.

## About the Stack

We started the full stack application for you. It is designed with some key functional areas:

### Backend
The [./backend](https://github.com/udacity/FSND/blob/master/projects/02_trivia_api/starter/backend/README.md) directory contains a partially completed Flask and SQLAlchemy server. You will work primarily in `__init__.py` to define your endpoints and can reference models.py for DB and SQLAlchemy setup. These are the files you'd want to edit in the backend:

1. *./backend/flaskr/`__init__.py`*
2. *./backend/test_flaskr.py*


### Frontend

The [./frontend](https://github.com/udacity/FSND/blob/master/projects/02_trivia_api/starter/frontend/README.md) directory contains a complete React frontend to consume the data from the Flask server. If you have prior experience building a frontend application, you should feel free to edit the endpoints as you see fit for the backend you design. If you do not have prior experience building a frontend application, you should read through the frontend code before starting and make notes regarding:

1. What are the end points and HTTP methods the frontend is expecting to consume?
2. How are the requests from the frontend formatted? Are they expecting certain parameters or payloads? 

Pay special attention to what data the frontend is expecting from each API response to help guide how you format your API. The places where you may change the frontend behavior, and where you should be looking for the above information, are marked with `TODO`. These are the files you'd want to edit in the frontend:

1. *./frontend/src/components/QuestionView.js*
2. *./frontend/src/components/FormView.js*
3. *./frontend/src/components/QuizView.js*


By making notes ahead of time, you will practice the core skill of being able to read and understand code and will have a simple plan to follow to build out the endpoints of your backend API. 



>View the [README within ./frontend for more details.](./frontend/README.md)


## API Documentation

### Getting Started
Base URL: https://localhost:5000/

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
Request URL:

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


Request URL:

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

Request URL:

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

Request URL:

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
