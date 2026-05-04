import os
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SeleniumWebDriverContextManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def __enter__(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()
        return False


def get_doughnut_data(driver) -> tuple[list, list]:
    result = driver.execute_script("""
        const plot = document.querySelectorAll('.js-plotly-plot')[0];
        const labels = plot._fullData[1].labels;
        const values = Array.from(plot._fullData[1].values);
        const hidden = plot._fullLayout.hiddenlabels || [];

        const filtered_labels = [];
        const filtered_values = [];
        labels.forEach((label, i) => {
            if (!hidden.includes(label)) {
                filtered_labels.push(label);
                filtered_values.push(values[i]);
            }
        });
        return { labels: filtered_labels, values: filtered_values };
    """)
    return result['labels'], result['values']


def save_doughnut_csv(labels: list, values: list, filename: str):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Facility Type", "Min Average Time Spent"])
        for label, value in zip(labels, values):
            writer.writerow([label, value])
    print(f"Saved chart data → {filename}")


if __name__ == "__main__":
    file_path = "report.html"

    with SeleniumWebDriverContextManager(headless=False) as driver:
        driver.get(f"file:///{os.path.abspath(file_path)}")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".js-plotly-plot"))
        )

        # Task 1 - table
        headers = driver.execute_script("""
            const plot = document.querySelector('.js-plotly-plot');
            return plot._fullData[0].header.values;
        """)
        columns = driver.execute_script("""
            const plot = document.querySelector('.js-plotly-plot');
            return plot._fullData[0].cells.values;
        """)

        with open("table.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for i in range(len(columns[0])):
                row = [columns[j][i] for j in range(len(columns))]
                writer.writerow(row)
        print("Saved table → table.csv")

        # Task 2 - chart
        driver.save_screenshot("screenshot0.png")
        print("Saved screenshot → screenshot0.png")

        labels, values = get_doughnut_data(driver)
        save_doughnut_csv(labels, values, "doughnut0.csv")

        try:
            toggles = driver.find_elements(By.CSS_SELECTOR, "g.legend rect.legendtoggle")
        except NoSuchElementException:
            raise RuntimeError("No chart filters found")

        for i, toggle in enumerate(toggles, start=1):
            try:
                toggle.click()
                import time

                time.sleep(1)

                # WebDriverWait(driver, 5).until(
                #     EC.presence_of_element_located((By.CSS_SELECTOR, "g.pielayer"))
                # )

                driver.save_screenshot(f"screenshot{i}.png")
                print(f"Saved screenshot → screenshot{i}.png")

                labels, values = get_doughnut_data(driver)

                if not values:
                    print(f"All filters are turned off — doughnut{i}.csv is empty.")
                    with open(f"doughnut{i}.csv", "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Facility Type", "Min Average Time Spent"])
                else:
                    save_doughnut_csv(labels, values, f"doughnut{i}.csv")

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error in the filter {i}: {e}")
                continue