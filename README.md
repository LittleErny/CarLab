Student 1: `Avrutskii, Mikhail`, `12306524`

Student 2: `Safronov, Mikhail`, `22305205`

# CarLab

[Link to the MyGit Repo](https://mygit.th-deg.de/ma06524/sas-thd)

[Link to the MyGit Wiki](https://mygit.th-deg.de/ma06524/sas-thd/-/wikis/home)

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
ToDo:
Explain how to start and use the project. Include steps for:
- Running the application.

## Implementation of the Requests

All the request are fully implemented. To see more detailed info, please visit Wiki. ToDo: add link here.

## Work Done
The work was split in the following way:
- Mikhail Avrutskii (2 accounts on Git: `LittleErny` & `Mikhail Avrutskii`)
    - Graphical User Interface & Visualization
    - General Data analysis
    - Sample dialogs
- Mikhail Safronov:
    - Strategies for outliers and fake data
    - Scikit-Learn
    - Dialog flow

