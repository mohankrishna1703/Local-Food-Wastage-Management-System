# Local Food Wastage Management System

---

## 💡 Project Overview

This project implements a **Local Food Wastage Management System**, a Streamlit-based web application designed to combat food waste by efficiently connecting surplus food providers with individuals and organizations in need. The system aims to streamline the donation process, reduce environmental impact, and address food insecurity within communities.

---

## ✨ Key Features

Our application provides a comprehensive set of functionalities to manage the food donation lifecycle:

* **Food Listing:** Providers (e.g., restaurants, caterers, households) can easily add details of surplus food items, including name, quantity, expiry date, food type (Vegetarian, Non-Vegetarian, Vegan), and meal type (Breakfast, Lunch, Dinner, Snacks).
* **Intuitive Filtering:** Receivers can effortlessly browse and filter available food listings based on various criteria like location, food type, and meal type to find what they need.
* **CRUD Operations:** Robust management capabilities allow providers to view, **update**, and **delete** their listed food items, ensuring accurate and up-to-date information.
* **Data Insights & Visualization:** A dedicated "Key Insights" section offers various analytical views and visualizations, including:
    * Providers and Receivers by City
    * Top Food Contributing Provider Types
    * Contact Information of Providers by City
    * Receivers Who Claimed the Most Food
    * Total Food Quantity Available
    * City with the Highest Number of Food Listings
    * Most Commonly Available Food Types
    * Percentage of Food Claims by Status
    * And many more valuable insights.
* **Database Integration:** Seamlessly interacts with an **SQLite database** (`food_wastage.db`) for persistent storage of all food listings, provider details, receiver information, and claims.

---

## 🛠️ Technologies Used

* **Frontend & Backend Framework:** [Streamlit](https://streamlit.io/) (for building interactive web applications in Python)
* **Database:** [SQLite3](https://www.sqlite.org/index.html) (lightweight, file-based SQL database)
* **Data Manipulation:** [Pandas](https://pandas.pydata.org/) (for data cleaning, analysis, and efficient interaction with the database)
* **Database Connector:** `sqlite3` (Python's built-in module for SQLite)
* **Version Control:** [Git](https://git-scm.com/) & [GitHub](https://github.com/)

---

## 🚀 Setup and Run Locally

Follow these steps to get a copy of the project up and running on your local machine.

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/mohankrishna1703/Local-Food-Wastage-Management-System.git](https://github.com/mohankrishna1703/Local-Food-Wastage-Management-System.git)
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd Local-Food-Wastage-Management-System
    ```
3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You might need to create a `requirements.txt` file first if you haven't already. You can generate it by running `pip freeze > requirements.txt` in your project folder.)*

### Database Setup

The project uses an SQLite database (`food_wastage.db`), which is included in the repository. If you need to regenerate it or ensure its structure, you would typically have a setup script or ensure the initial data is populated (e.g., from CSVs mentioned in the project). For this project, the `food_wastage.db` file should be present and sufficient.

### Running the Application

1.  **Start the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
2.  Your default web browser should automatically open to the Streamlit application (usually at `http://localhost:8501`).

---

## 📋 How to Use the Application

Once the application is running:

* **Navigation:** Use the sidebar to navigate between "Key Insights", "Filter Food Listings", "Add New Food Listing", and "Manage Food Listings".
* **Add New Food Listing:** Fill out the form to add new surplus food items.
* **Filter Food Listings:** Use the dropdowns to search for specific food items based on location, type, and meal.
* **Manage Food Listings:** Select an existing listing to update its details or delete it.
* **Key Insights:** Explore various charts and tables that provide analytical views of the food data.

---

## 📂 Project Structure