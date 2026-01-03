import time
import pandas as pd 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def get_status_from_icon(element):
    try:
        cls = element.get_attribute("class")
        style = element.get_attribute("style")
        if "css-hcqxoa" in cls or "check" in cls:
            return "yes"
        elif "css-1kiw93k" in cls or "x" in cls:
            return "no"
        elif "css-10sviso" in cls or "line" in cls or "circle" in cls:
            return "Neutral"
        else:
            return "N/A"
    except:
        return "N/A"


def Scrape_glassdor():
    target_url = "https://www.glassdoor.co.in/Reviews/Blackcoffer-Reviews-E2260916.htm"
    pages_to_scrape = 20
    proxy = 'RESIDENTIAL_PROXY_IP:PORT'
    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server={proxy}')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get(target_url)
    print("="*60)
    print("Please login manually")
    print("Maviagte to the reviews page after login")
    print("Press enter in the terminal after completing the login and navigation")
    print("="*60)
    input("Press Enter to continue...")

    all_data = []

    for page in range(pages_to_scrape):
        print(f"Processing Page {page+1}")
        time.sleep(3)

        try:
            more_links = driver.find_elements(By.XPATH, "//div[contains(text(), 'see more')]")
            for link in more_links:
                driver.execute_script("arguments[0].click();", link)
                time.sleep(0.5)

            for drop in dropdowns:
                try:
                    driver.execute_script("arguments[0].click();", drop)
                    time.sleep(0.2)
                except:
                    pass

        except Exception as e:
            print(f"Error expanding reviews: {e}")

        reviews = driver.find_elements(By.CLASS_NAME, "empReview")

        for review in reviews:
            row = {}
            try:
                row['Overall rating'] = review.find_element(By.CLASS_NAME, 'ratingNumber').text
            except:
                row['Overall rating'] = "N/A"
            try:
                row['Feedback'] = review.find_element(By.CLASS_NAME, "title").text
            except:
                row['Feedback'] = "N/A"
            try:
                row['Date'] = review.find_element(By.CLASS_NAME, "authorJobTitle").text.split('-')[0].strip()
            except:
                row['Date'] = "N/A"
            try:
                job_line = review.find_element(By.CLASS_NAME, "authorJobTtitle").text
                row['Position'] = job_line.split('-')[1].strip() if '-' in job_line else job_line
                row['Service time'] = job_line
            except:
                row['Position'] = "N/A"
                row['Service time'] = "N/A"
            try:
                row['location'] = review.find_element(By.CLASS_NAME, "authorLocation").text
            except:
                row['location'] = "N/A"

            sub_ratings_map = {
                "Diversity and Inclusion": 'N/A',
                "Career Opportunities": 'N/A',
                "Culture and Values": 'N/A',
                "Work/Life Balance": "N/A",
                "Senior Management": 'N/A',
                "Compensation and Benefits": 'N/A'
            }

            try:
                sub_rating_items = review.find_elements(By.CSS_SELECTOR, "ul.undecorated > li")
                for item in sub_rating_items:
                    text = item.text
                    for key in sub_ratings_map.keys():
                        if key.lower() in text.lower():
                            sub_ratings_maps[key] = "Present (Check manual)"
            except:
                pass
            
            for k, v in sub_ratings_map.items():
                row[k] = v

            try:
                row['Pros'] = review.find_element(By.XPATH, ".//span[@data-test='pros']").text
            except:
                row['Pros'] = "N/A"
            try:
                row['Cons'] = review.find_element(By.XPATH, ".//span[@data-test='cons']").text
            except:
                row['Cons'] = "N/A"

            try:
                reco_section = review.find_elements(By.CLASS_NAME, "recommends")
                if reco_section:
                    text_content = reco_section[0].text
                    row['Recommend'] = "Yes" if "Recommend" in text_content and "Doesn't Recommend" not in text_content else "No"
                    row['CEO Approval'] = "Yes" if "CEO Approval" in text_content else "N/A"
                    row['Business Outlook'] = "Yes" if "Business Outlook" in text_content else "N/A"
                else:
                    row['Recommend'] = "N/A"
                    row['CEO Approval'] = "N/A"
                    row['Business Outlook'] = "N/A"
            except:
                row['Recommend'] = "N/A"
                row['CEO Approval'] = "N/A"
                row['Business Outlook'] = "N/A"
            
            row['URL'] = driver.current_url
            all_data.append(row)

            try:
                next_btn = driver.find_element(By.XPATH, ".//button[@data-test='pagination-next']")
                if not next_btn.is_enabled(): break
                next_btn.click()
            except:
                print("No more pages or error navigating to next page.")
        driver.quit()

        df = pd.DataFrame(all_data)

        desired_order = [
            'Overall rating', 'Feedback', 'Position', 'Service time', 'Diversity and Inclusion',
            'Career Opportunities', 'Culture and Values', 'Work/Life Balance', 'Senior Management',
            'Compensation and Benefits', 'Pros', 'Cons', 'Recommend', 'CEO Approval', 'Business Outlook',
            'Date','URL'
        ]

        for col in desired_order:
            if col not in df.columns:
                df[col] = "N/A"

        df = df[desired_order]

        df.to_excel("glassdoor_reviews.xlsx", index=False)
        print("Data saved to glassdoor_reviews.xlsx")


if __name__ == "__main__":
    Scrape_glassdor()