# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

Our platform is dedicated to seamlessly bridging the gap between donors and charities, ensuring transparency, and ease of donation management.

## User stories
[Issues](https://github.com/software-students-fall2023/2-web-app-exercise-isomorphism/issues)
- As a donor, I want to provide my donations so that I can support the causes I care about.
- As a donor, I want to edit my previous donations so that I ensure accuracy and update any necessary details.
- As a donor, I want to delete any of my donations so that I can correct mistakes or change my mind about certain contributions.
- As a charity, I want to search for donations based on specific criteria so that I can better manage and allocate resources.
- As a donor, I want to view all of my donations in one place so that I can track my overall charitable contributions.
- As a charity, I want to view all donations so that I can choose the appropriate ones to accept.
- As a prospective donor or charity, I want to register on the platform so that I have the ability to either give or receive donations.

## Task boards

[Task Board 1](https://github.com/orgs/software-students-fall2023/projects/1)  
[Task Board 2](https://github.com/orgs/software-students-fall2023/projects/50)

## How to Run Our Web-App

### Prerequisites

- [Python](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop)

### Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/software-students-fall2023/2-web-app-exercise-isomorphism
```

#### 2. Set Up a Virtual Environment

```bash
python -m venv .venv
```

For **Windows**:

```bash
.venv\Scripts\activate
```

For **macOS/Linux**:

```bash
source .venv/bin/activate
```

#### 3. Install the Required Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Start MongoDB using Docker

Run the following command to host MongoDB locally using Docker:

```bash
docker run --name mongodb_dockerhub -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret -d mongo:latest
```

#### 5. Run the Web-App

After setting up MongoDB, you can start the web-app (ensure running this command in the virtual environment with the dependencies):

```bash
python app.py
```

The web-app should now be running on `http://127.0.0.1:5000/`. Open the link in your preferred web browser.

### Functionality Breakdown

This web-app serves as a streamlined donation platform offering functionalities tailored for both donors and charities. 

#### Features for Donors:

- **Register as a Donor**: Get started by creating a donor account.
- **Add Donations**: Provide details about the items you wish to donate.
- **View My Donations**: Access a list of all the donations you've made.
  - **Edit Donations**: Update donation details as needed.
  - **Delete Donations**: Choose to remove a donation from the list.

#### Features for Charities:

- **Register as a Charity**: Create an account to represent your charitable organization.
- **View All Available Donations**: Browse through the comprehensive list of donations.
- **Search Donations**: Find specific donations using relevant keywords or filters.
- **Accept Donations**: Choose and accept the donations suitable for your charity's mission.

### Conclusion
For any issues or further assistance, please feel free to contact us!
