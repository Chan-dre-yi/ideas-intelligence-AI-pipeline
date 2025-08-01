'''
This script uses web-scraping libraries,
& scrapes out ideas 
from the given intel URL, into a csv.
It implements microsoft SSO login in auto-pilot,
to get access to the internal site data.
'''



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import getpass
import time
import pandas as pd
from ftfy import fix_text
from urllib.parse import urlparse




########################

em = "" #add the email ID to be used for microsoft SSO login
ps = "" #add the password to the given email
link = "" #add the URL the comments are to be scraped from
f = "" #add the csv file name (x.csv) or path with name, you want the comments and replies to be stored in


########################




# def login_microsoft_sso(target_url):
#     # email = input("Enter your corporate email: ")
#     email = em
#     # password = getpass.getpass("Enter your password: ")
#     password = ps

#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("--incognito")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--start-maximized")

#     driver = webdriver.Chrome(options=chrome_options)
#     driver.get(target_url)

#     WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "i0116"))).send_keys(email)
#     driver.find_element(By.ID, "idSIButton9").click()

#     WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "i0118"))).send_keys(password)
#     driver.find_element(By.ID, "idSIButton9").click()

#     try:
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click()
#     except:
#         pass

#     return driver

def login_microsoft_sso(target_url):
    # email = input("Enter your corporate email: ")
    email = em  # Replace with your email
    # password = getpass.getpass("Enter your password: ")
    password = ps  # Replace with your password

    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("--incognito")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--start-maximized")

    # Use Microsoft Edge WebDriver
    driver = webdriver.Edge(options=edge_options)
    driver.get(target_url)

    # Wait for email input and enter the email
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "i0116"))).send_keys(email)
    driver.find_element(By.ID, "idSIButton9").click()

    # Wait for password input and enter the password
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "i0118"))).send_keys(password)
    driver.find_element(By.ID, "idSIButton9").click()

    # Handle "Stay signed in?" prompt (if it appears)
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click()
    except:
        pass

    return driver






# fetch decription too
def extract_ideas_votes(driver):
    data = []

# Set items per page to 100
    # try:
    #     # Click the page size dropdown (e.g. "10 / page")
    #     page_size_dropdown = WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.CSS_SELECTOR, "span.ant-select-selection-item[title*='/ page']"))
    #     )
    #     page_size_dropdown.click()

    #     # Click the "100 / page" option
    #     option_100 = WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select-item-option')][.='100 / page']"))
    #     )
    #     option_100.click()

    #     time.sleep(1.5)  # Wait for table to refresh
    # except Exception as e:
    #     print(f"⚠️ Could not set items per page to 100: {e}")


    while True:
        time.sleep(2)  # let table load

        rows = driver.find_elements(By.CSS_SELECTOR, "tbody.ant-table-tbody > tr.ant-table-row")

        for row_index in range(len(rows)):
            # Re-fetch rows each time, because DOM is refreshed after back()
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody.ant-table-tbody > tr.ant-table-row")
            row = rows[row_index]

            try:
                idea_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) div.ant-typography")
                idea = idea_element.text.strip()
                driver.execute_script("arguments[0].click();", idea_element)
            except:
                idea = ""
                continue  # skip this row if it can't be clicked

            time.sleep(2)  # wait for new page to load

            # Extract description from detail page
            try:
                description_elem = driver.find_element(By.CSS_SELECTOR, "div._markdown_11j0i_1")
                description = description_elem.text.strip()
            except:
                description = ""

            # Extract segment, votes, created – assuming these are visible on main table only
            # so you’ll need to store them before navigating if not available on detail page
            # Otherwise, re-grab them on the previous page (next step)

            driver.back()
            time.sleep(2)  # wait for table page to reload

            # Re-fetch the row to get other fields
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody.ant-table-tbody > tr.ant-table-row")
            row = rows[row_index]

            try:
                segment = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()
            except:
                segment = ""

            try:
                votes = row.find_element(By.CSS_SELECTOR, "td:nth-child(3)").text.strip()
            except:
                votes = "0"

            try:
                created = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)").text.strip()
            except:
                created = ""

            data.append({
                "Idea": idea,
                "Segment": segment,
                "Votes": votes,
                "Created": created,
                "Description": description
            })

        # Try to go to next page
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.ant-pagination-next")
            aria_disabled = next_button.get_attribute("aria-disabled")
            if aria_disabled == "true":
                break  # No more pages
            else:
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
        except:
            break

    return data







def save_to_csv(data, filename=f):
    df = pd.DataFrame(data)
    df['Idea'] = df['Idea'].astype(str).apply(fix_text)
    df.to_csv(filename, index=False)
    print(f"✅ Extracted {len(df)} ideas. Saved to '{filename}'.")


if __name__ == "__main__":
    driver = webdriver.Edge()
    driver.get(link)  # Replace with your actual target page
    time.sleep(5)  # Adjust depending on how long it takes to load/login

    ideas_votes = extract_ideas_votes(driver)
    save_to_csv(ideas_votes)

    driver.quit()
    

