# Viva Questions and Answers

## General Project (10 Questions)

**1. What is the title of your project and what is its primary goal?**
My project is titled "AI-Based Attendance Management System." Its primary goal is to automate the process of recording student attendance in educational institutions using facial recognition technology, eliminating manual roll calls and paper registers.

**2. Why did you choose face recognition over other biometric methods like fingerprints?**
Face recognition is contactless, which solves hygiene concerns and prevents physical bottlenecks at classroom entrances. It also requires no specialized hardware, as it can operate using standard webcams or IP cameras that institutions may already have installed.

**3. What exact problem does your system solve?**
It solves three main problems: the immense time wasted during manual roll calls, the issue of "proxy" attendance where students sign in for absent friends, and the administrative overhead of manually compiling attendance reports.

**4. Who are the intended users of this system?**
The system has two primary users: Administrators, who manage the overall student database and system configurations, and Faculty members, who initiate attendance sessions and view course-specific reports.

**5. Can you explain the basic workflow of your application?**
An admin registers a student by capturing their face and generating an embedding. Later, a faculty member starts an attendance session for a specific subject. The system captures the webcam feed, detects faces, matches them against the database, and automatically logs the recognized students as present.

**6. What happens if the system fails to recognize a student who is actually present?**
The system includes a manual override feature. Faculty members can monitor the live attendance list and manually mark a student as present if the AI fails to recognize them due to poor lighting or occlusion.

**7. How is your system better than scanning QR codes for attendance?**
QR codes can easily be photographed and shared via messaging apps, allowing students to scan the code from their dorm room, which completely defeats the purpose. Facial recognition requires the physical biometric presence of the student.

**8. What is the overall architecture of your project?**
It follows a client-server architecture. The frontend is a Single Page Application built in React. It communicates via RESTful APIs with a FastAPI backend. The backend handles database operations using SQLAlchemy and processes images using a Machine Learning pipeline based on dlib and OpenCV.

**9. Did you build the facial recognition model from scratch?**
No, training a highly accurate model from scratch requires massive datasets and compute power. We utilized a pre-trained ResNet model provided by the dlib library, which is highly optimized and widely regarded as state-of-the-art for generating facial embeddings.

**10. What was the most challenging part of developing this system?**
The most challenging part was optimizing the machine learning pipeline to run fast enough for real-time processing while maintaining high accuracy, specifically tuning the distance thresholds and handling varying lighting conditions in the video feed.

## Machine Learning (10 Questions)

**11. What is the difference between face detection and face recognition?**
Face detection is the process of locating a human face within an image and drawing a bounding box around it. Face recognition is the subsequent step of identifying *whose* face it is by comparing its features against a known database.

**12. What algorithm did you use for Face Detection?**
We primarily used the HOG (Histogram of Oriented Gradients) algorithm. It provides an excellent balance between computational speed and accuracy, allowing the system to process video frames in real-time on standard CPU hardware.

**13. How does the 128-dimensional embedding work?**
Once a face is detected, a Convolutional Neural Network (CNN) analyzes it and outputs a list of 128 numbers. This vector acts as a unique mathematical "fingerprint" of the face. Faces of the same person will produce very similar vectors, while different people will produce vastly different vectors.

**14. What distance metric do you use to compare faces?**
We use Euclidean distance to compare the 128-d embeddings. It calculates the straight-line mathematical distance between the two vectors in 128-dimensional space. A smaller distance means the faces are more similar.

**15. What threshold did you choose for face matching and why?**
We chose a threshold of 0.6. Through empirical testing, a distance strictly less than 0.6 provided the best balance, minimizing false positives (recognizing the wrong person) while keeping false negatives (failing to recognize the right person) reasonably low.

**16. What are FAR and FRR?**
FAR stands for False Acceptance Rate, which is the percentage of times the system incorrectly matches an unknown face to a registered user. FRR is False Rejection Rate, the percentage of times it fails to recognize a genuinely registered user.

**17. What is Liveness Detection and why is it necessary?**
Liveness detection ensures that the face presented to the camera is a real, live human and not a photograph or video played on a phone screen. It is necessary to prevent spoofing attacks.

**18. What is EAR (Eye Aspect Ratio)?**
EAR is a mathematical calculation based on the distance between facial landmarks around the eyes. It is used in liveness detection to track blinking. A sudden drop and rise in the EAR value indicates a natural blink, proving liveness.

**19. How does your system handle multiple faces in a single frame?**
The HOG detector scans the entire image and returns an array of bounding boxes for all detected faces. The system then loops through this array, extracting embeddings and performing recognition for each face individually within the same frame.

**20. How do you handle lighting variations?**
Before passing the image to the neural network, the system performs preprocessing steps like converting the image to grayscale or applying histogram equalization to normalize the contrast and mitigate the effects of harsh lighting or shadows.

## Backend/API (8 Questions)

**21. Why did you choose FastAPI for the backend?**
FastAPI is highly performant because it supports asynchronous programming out of the box. It also heavily utilizes Python type hints, which reduces bugs, and automatically generates interactive API documentation (Swagger UI), which sped up frontend integration.

**22. What is JWT and how do you use it?**
JWT stands for JSON Web Token. Upon successful login, the backend generates a signed JWT containing the user's ID and role. The frontend stores this token and sends it in the Authorization header of subsequent requests to prove identity.

**23. How do you handle authentication in FastAPI?**
We use FastAPI's `Depends` injection system. We created a dependency function that intercepts incoming requests, extracts the JWT from the header, validates the signature, and retrieves the corresponding user from the database. If invalid, it throws a 401 Unauthorized error.

**24. What is CORS and why did you need to configure it?**
CORS (Cross-Origin Resource Sharing) is a browser security feature. Because our React frontend runs on port 3000 and our FastAPI backend on port 8000, they are considered different "origins." We had to configure the backend CORS middleware to explicitly allow requests from the frontend origin.

**25. How does your backend handle file uploads for face registration?**
FastAPI provides an `UploadFile` class. When a photo is uploaded from the frontend, it is received as binary data in memory. We read this data, decode it into an OpenCV image format, process it to extract the embedding, and then discard the raw image.

**26. What is SQLAlchemy and why use it?**
SQLAlchemy is an Object-Relational Mapper (ORM) for Python. It allows us to interact with the database using Python classes and objects instead of writing raw SQL queries. This makes the code cleaner, prevents SQL injection, and makes it easy to switch databases (e.g., from SQLite to PostgreSQL).

**27. How are database relationships handled in SQLAlchemy?**
We use the `relationship()` function provided by SQLAlchemy. For example, a `Student` model has a relationship to `AttendanceRecords`, allowing us to easily access a student's entire attendance history as a Python list property.

**28. What is Alembic?**
Alembic is a database migration tool used alongside SQLAlchemy. When we change our Python database models (like adding a new column), Alembic generates a migration script that updates the actual database schema safely without losing existing data.

## Frontend (5 Questions)

**29. Why did you choose React.js?**
React allows for building complex, interactive user interfaces using reusable components. Its virtual DOM ensures fast rendering, which is crucial for smoothly displaying a live webcam feed alongside dynamic data tables.

**30. What is Tailwind CSS?**
Tailwind is a utility-first CSS framework. Instead of writing custom CSS classes, we apply pre-defined utility classes directly to HTML elements (like `bg-blue-500` or `p-4`). It drastically speeds up styling and ensures a consistent design system.

**31. How does the webcam integration work in React?**
We utilized a library like `react-webcam`. It taps into the browser's `navigator.mediaDevices.getUserMedia` API to access the camera hardware. We use a React `ref` to periodically capture the current frame as a base64 encoded image string to send to the backend.

**32. What is React Router used for?**
React Router enables navigation within our Single Page Application. It allows us to define different URLs (like `/dashboard`, `/students`, `/attendance`) and render different React components based on the URL without requiring a full page reload from the server.

**33. How do you handle state management?**
For local component state (like form inputs or toggle switches), we use React's `useState` hook. For passing data down multiple levels (like the authenticated user's profile), we utilize React's Context API.

## Database (5 Questions)

**34. Why use SQLite for development?**
SQLite is a serverless, file-based database. It requires zero configuration, making it incredibly fast and easy to set up during the development phase.

**35. Can you briefly explain your ER diagram?**
We have core entities like `Users` (faculty/admins) and `Students`. A `Subject` has many `AttendanceSessions`. Each Session contains multiple `AttendanceRecords`. An `AttendanceRecord` is a junction table linking a specific `Student` to a specific `Session` with a timestamp.

**36. What is database normalization and is your schema normalized?**
Normalization is the process of organizing data to reduce redundancy and improve data integrity. Yes, our schema is in 3rd Normal Form. For example, student details are stored once in the `Students` table, and `AttendanceRecords` only reference the student ID, not their name.

**37. How do you store the face embeddings in the database?**
The 128-dimensional embedding is essentially a list of floating-point numbers. We serialize this list into a JSON string or store it as a binary BLOB in the `FaceEmbeddings` table, linked to the student's ID via a foreign key.

**38. What happens to attendance records if a student is deleted?**
We use cascading deletes. If a student is removed from the database, the foreign key constraints ensure that their associated face embeddings and attendance records are either automatically deleted or safely archived, preventing orphaned data.

## Security (5 Questions)

**39. How do you secure user passwords?**
We never store plain-text passwords. We use the `bcrypt` hashing algorithm. Bcrypt incorporates a "salt" (random data) and is intentionally slow, making it highly resistant to brute-force and dictionary attacks.

**40. What are SQL injection risks and how are they mitigated?**
SQL injection is when an attacker inputs malicious SQL commands into a form to manipulate the database. We are protected because we use SQLAlchemy ORM, which automatically parameterizes queries, treating user input strictly as data, never as executable code.

**41. How does Role-Based Access Control (RBAC) work in your system?**
When a user logs in, their JWT includes their role (e.g., 'admin' or 'faculty'). FastAPI endpoint dependencies check this role. If a 'faculty' user tries to access a POST route meant for registering students (an admin-only task), the API rejects the request with a 403 Forbidden status.

**42. How do you handle the privacy of biometric data?**
We strictly adhere to data minimization. We do not save or store the raw images or video frames of students. Once an image is processed into a mathematical embedding, the image is discarded. Embeddings cannot be reverse-engineered to reconstruct a face.

**43. Is the API communication secure?**
In a production deployment, the entire application, including API endpoints, must be served over HTTPS. This encrypts the data in transit, ensuring that JWT tokens or image frames cannot be intercepted via man-in-the-middle attacks.

## Testing (3 Questions)

**44. What testing framework did you use for the backend?**
We used `pytest`. It is a robust Python testing framework that allows us to write simple, readable test cases for our API endpoints, database interactions, and utility functions.

**45. How do you test the ML components?**
We test ML components using a validation dataset of known faces. We run the recognition pipeline against this dataset and calculate precision, recall, and accuracy metrics to ensure changes to the code or thresholds do not negatively impact performance.

**46. What is test coverage?**
Test coverage is a metric that measures the percentage of our source code that is executed during our automated tests. We use plugins like `pytest-cov` to identify untested parts of our application to ensure maximum reliability.

## Deployment (4 Questions)

**47. What is Docker and why use it?**
Docker is a containerization platform. It packages our application (backend, frontend, ML dependencies) into standardized units called containers. This guarantees that the software will run exactly the same way on a deployment server as it did on our local development machines, eliminating "it works on my machine" issues.

**48. How does docker-compose work in this project?**
`docker-compose.yml` is a configuration file that defines multiple Docker containers. We use it to orchestrate our frontend container, backend container, and potentially a database container, allowing us to build and start the entire system with a single command.

**49. What is CI/CD?**
CI/CD stands for Continuous Integration and Continuous Deployment. It's a DevOps practice. Using tools like GitHub Actions, every time code is pushed, tests are automatically run (CI), and if successful, the new version is automatically deployed to the server (CD).

**50. How would you deploy this to a cloud environment?**
For production, we would provision a cloud server (like AWS EC2 or DigitalOcean Droplet). We would switch the database to PostgreSQL, set up Nginx as a reverse proxy to serve the React frontend and route API requests, and secure it with an SSL certificate using Let's Encrypt.
