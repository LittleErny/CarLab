# CarLab

The project was implemented by me, [Mikhail Avrutskii](https://github.com/LittleErny), and [Mikhail Safronov](https://github.com/MikeSafronov42) as a part of Assistance Systems course at [Deggendorf Institute of Technology](https://th-deg.de/en).  

[Link to the initial MyGit Repo](https://mygit.th-deg.de/ma06524/sas-thd)

[Link to the initial MyGit Wiki](https://mygit.th-deg.de/ma06524/sas-thd/-/wikis/home)

## Project Description
Our project fulfills several objectives:

First, it is aimed at beginner Data Science enthusiasts who would like to understand what Data Science is in an interactive format. This is demonstrated through a case study of the German used car market in 2016. The project provides extensive opportunities to explore the dataset and experiment with various machine learning methods, guiding users at each step and explaining unclear points.

Second, the project offers comprehensive analytics of the German used car market in 2016. With these analytics, users can learn almost anything—from the average mileage of cars sold to the price of their dream car in 2016.

Third, the project provides consulting services in the form of a chat. Our chatbot helps users choose a car and provides guidance on prices, features, and the market in general.

## Installation
1. Make sure to have Python 3.9.13 installed. Some of included packages and libraries have very tight requirements, this is why we do not guarantee proper work on other versions.

2. **Copy repo to your PC**:

   ```bash
   git clone https://mygit.th-deg.de/ma06524/sas-thd
   cd sas-thd
   ```

 3. **Create a virtual environment:**
   - For Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - For macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

4. **Install required libraries from `requirements.txt`:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify the installation:**
   Ensure all dependencies are installed by checking the versions:
   ```bash
   python --version
   pip list
   pip check
   ```

To run the app, see the **Basic Usage** section.

## Data
The Dataset used in our project can be found on [Kaggle](https://www.kaggle.com/datasets/shaunoilund/auto-sales-ebay-germany-random-50k-cleaned/) free of charge. The dataset is distributed with *CC0 1.0 Universal* Linence, which allows copying, modifying, distributing and performing the work without asking permission. 

If you want to see the data description, as well as approaches of handling outliers and creating fake data, please see the [Data](https://mygit.th-deg.de/ma06524/sas-thd/-/wikis/Data) page in our Wiki or run the project.


## Basic Usage

**Running the application:**

1. Open a terminal on your system.
2. Navigate to the project folder using the `cd` command. For example:
   ```bash
   cd /path/to/project-folder
   ```
3. Run the following command to start the application:
   ```bash
   streamlit run Hello.py
   ```
4. Once the application is running, a browser window should open automatically displaying the app. If not, you can copy the provided URL from the terminal and paste it into your browser.

**Using the Rasa ChatBot:**

1. Navigate to the **ChatBot** page in the Streamlit application.
2. When you access this page, two additional terminal windows will appear:
   - One for the Rasa server.
   - Another for the Rasa action server.
3. Wait until both terminals display a success message indicating that the Rasa ChatBot is ready.
4. Once both terminals show success messages, you can start chatting with the ChatBot directly from the application.

## The split of the roles in the project
Generally, the work was split in the following way:
- Mikhail Avrutskii (2 usernames on Git: `LittleErny` & `Mikhail Avrutskii`)
    - Graphical User Interface & Visualization
    - General Data analysis
    - Sample dialogs
- Mikhail Safronov:
    - Strategies for outliers and fake data
    - Scikit-Learn
    - Dialog flow

However, refer to [this](https://mygit.th-deg.de/ma06524/sas-thd/-/wikis/Implementation-of-Requests) Wiki page to see the exact work split.

## Video Demonstration

You can find the video demostration of our project [here](https://mygit.th-deg.de/ma06524/sas-thd/-/tree/main/Video%20Demonstration).
