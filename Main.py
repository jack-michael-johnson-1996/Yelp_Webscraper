from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import API
import pandas as pd
import time
import os
import csv

chrome_options = Options()
chrome_options.headless = True

driver = webdriver.Chrome(executable_path=os.getcwd() + r"\chromedriver.exe", options=chrome_options)
# to maximize the browser window
driver.maximize_window()
timeout = 120

keyWords = ["noise", "noisy", "loud", "too loud", "music loud", "music too loud"]

def importData(csv_filename):
    data = pd.read_csv(os.getcwd() + "\\" + csv_filename, )

    with open('Output.csv', 'a', newline='') as csvfile:
        fieldnames = ['Name', 'Location', 'Stars', 'Review', 'Total', 'New Name', 'ID', 'Address New']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    with open('Output_NR.csv', 'a', newline='') as csvfile:
        fieldnames = ['Name', 'Location', 'Total', 'New Name', 'ID', 'Address New']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    return data


def searchVenue(venue, location):

    try:
        venue_API, venue_id, location_new = API.API(venue, location)
        URL = "https://www.yelp.com/biz/" + venue_id
        driver.get(URL)
        #current_url = driver.current_url
        #new_url = current_url + "?osq=q"
        #driver.get(new_url)
        return venue_API, venue_id, location_new

    except:
        try:
            driver.get("https://www.yelp.com")
            findBox = driver.find_element_by_id("find_desc")
            findBox.send_keys(venue)
            nearBox = driver.find_element_by_id("dropperText_Mast")
            nearBox.clear()
            nearBox.send_keys(location)
            searchButton = driver.find_element_by_id("header-search-submit")
            searchButton.click()
            venueLink = driver.find_element_by_xpath("//a[@name='" + venue + "']")
            venueLink.click()
            return venue, "", location

        except:
            try:
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight/5)")
                venueLink = driver.find_element_by_xpath("//a[@name='" + venue + "']")
                venueLink.click()
                return venue, "", location
            except:
                raise


def scrapeReviewTotal(venue, location):
    try:
        totalReviews = driver.find_element_by_class_name('css-bq71j2').text
        element_present = EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "css-1joxor6"))
        WebDriverWait(driver, timeout).until(element_present)
        NR_totalReviews = driver.find_element_by_class_name('css-1joxor6').text
        NR_totalReviews_r = NR_totalReviews.replace(" other reviews that are not currently recommended","")
        #print(len(totalReviews))
        if len(totalReviews) == 8:
            totalReviews = int(totalReviews[:-6])
            #print(totalReviews)
            totalReviews += int(NR_totalReviews_r)
        else:
            totalReviews = int(totalReviews[:-8])
            totalReviews += int(NR_totalReviews_r)

    except:
        try:
            time.sleep(1)
            totalReviews = driver.find_element_by_class_name('css-bq71j2').text
            element_present = EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "css-1joxor6"))
            WebDriverWait(driver, timeout).until(element_present)
            NR_totalReviews = driver.find_element_by_class_name('css-1joxor6').text
            NR_totalReviews_r = NR_totalReviews.replace(" other reviews that are not currently recommended", "")

            if len(totalReviews) == 8:
                totalReviews = int(totalReviews[:-6])
                totalReviews += int(NR_totalReviews_r)

            else:
                totalReviews = int(totalReviews[:-8])
                totalReviews += int(NR_totalReviews_r)

        except:
            try:
                time.sleep(5)
                totalReviews = driver.find_element_by_class_name('css-bq71j2').text
                element_present = EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "css-1joxor6"))
                WebDriverWait(driver, timeout).until(element_present)
                NR_totalReviews = driver.find_element_by_class_name('css-1joxor6').text
                NR_totalReviews_r = NR_totalReviews.replace(" other reviews that are not currently recommended", "")

                if len(totalReviews) == 8:
                    totalReviews = int(totalReviews[:-6])
                    totalReviews += int(NR_totalReviews_r)

                else:
                    totalReviews = int(totalReviews[:-8])
                    totalReviews += int(NR_totalReviews_r)

            except:
                print("Error: could not find review total for {0} in {1}. Total skipped.".format(venue, location))
                totalReviews = 0

    return totalReviews


def scrapeNonRecommended(name, location, id, totalReviews, newName, address_new):
    URL_NR = "https://www.yelp.com/not_recommended_reviews/" + id
    driver.get(URL_NR)
    element_present = EC.presence_of_all_elements_located((By.TAG_NAME, "h3"))
    WebDriverWait(driver, timeout).until(element_present)
    #element_present2 = EC.presence_of_all_elements_located((By.CLASS_NAME, "review-wrapper"))
    #WebDriverWait(driver, timeout).until(element_present2)

    reviewBox = driver.find_elements_by_class_name("ysection")
    reviewBox2 = reviewBox[1].find_element_by_tag_name("h3")
    TotalReviews_NR = reviewBox2.text
    #print(TotalReviews_NR)
    venueURL = driver.current_url
    scrubbedReviews = 0

    #driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    #print(TotalReviews_NR)

    if int(TotalReviews_NR[0]) == 0:
        return 0
    else:
        pages = driver.find_element_by_class_name("page-of-pages").text
        pages = int(pages[9:])
        #print(pages)

        currentPage = 0
        increment = 0

        if pages != 1:
            for page in range(pages):
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                element_present = EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "ysection"))
                WebDriverWait(driver, timeout).until(element_present)
                element_present2 = EC.presence_of_all_elements_located((By.CLASS_NAME, "review-wrapper"))
                WebDriverWait(driver, timeout).until(element_present2)
                reviewBox = driver.find_elements_by_class_name("ysection")
                NR_Reviews = reviewBox[1].find_elements_by_class_name("review-content")
                #print(NR_Reviews.text)

                #lastPage = int(pages[5:])
                # print(lastPage)


                for i in range(len(NR_Reviews)):
                    reviewBox = driver.find_elements_by_class_name("ysection")
                    NR_Reviews = reviewBox[1].find_elements_by_class_name("review-content")
                    innerHTML = NR_Reviews[i].get_attribute('innerHTML')

                    if "title=\"1.0 star rating\"" in innerHTML:
                        reviewText = NR_Reviews[i].find_element_by_tag_name("p").text
                        #print(reviewText)
                        reviewText_lower = reviewText.lower()
                        stars = 1
                        for w in keyWords:
                            if w in reviewText_lower:
                                #print(reviewText_lower)
                                with open('Output.csv', 'a', newline='') as csvfile:
                                    fieldnames = ['Name', 'Location', 'Stars', 'Review', 'Total', 'New Name', 'ID', 'Address New']
                                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                    writer.writerow({'Name': name, 'Location': location, 'Stars': stars,
                                                     'Review': reviewText, 'Total': totalReviews, 'New Name': newName,
                                                     'ID': id, 'Address New': address_new})
                                scrubbedReviews += 1

                    elif "title=\"2.0 star rating\"" in innerHTML:
                        reviewText = NR_Reviews[i].find_element_by_tag_name("p").text
                        reviewText_lower = reviewText.lower()
                        stars = 2
                        for w in keyWords:
                            if w in reviewText_lower:
                                #print(reviewText_lower)
                                with open('Output.csv', 'a', newline='') as csvfile:
                                    fieldnames = ['Name', 'Location', 'Stars', 'Review', 'Total', 'New Name', 'ID', 'Address New']
                                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                    writer.writerow({'Name': name, 'Location': location, 'Stars': stars,
                                                     'Review': reviewText, 'Total': totalReviews, 'New Name': newName,
                                                     'ID': id, 'Address New': address_new})
                                scrubbedReviews += 1

                currentPage += 1

                if currentPage == pages:
                    break

                increment += 10
                currentURL = venueURL + "?not_recommended_start=" + str(increment)
                driver.get(currentURL)
                element_present = EC.presence_of_all_elements_located((By.CLASS_NAME, 'ysection'))
                WebDriverWait(driver, timeout).until(element_present)
                element_present2 = EC.presence_of_all_elements_located((By.CLASS_NAME, 'review-content'))
                WebDriverWait(driver, timeout).until(element_present2)
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

        else:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            element_present = EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "ysection"))
            WebDriverWait(driver, timeout).until(element_present)
            element_present2 = EC.presence_of_all_elements_located((By.CLASS_NAME, "review-wrapper"))
            WebDriverWait(driver, timeout).until(element_present2)
            reviewBox = driver.find_elements_by_class_name("ysection")
            NR_Reviews = reviewBox[1].find_elements_by_class_name("review-content")

            for i in range(len(NR_Reviews)):

                innerHTML = NR_Reviews[i].get_attrisbute('innerHTML')

                if "title=\"1.0 star rating\"" in innerHTML:
                    reviewText = NR_Reviews[i].find_element_by_tag_name("p").text
                    #print(reviewText)
                    reviewText_lower = reviewText.lower()
                    stars = 1
                    #print(stars)
                    for w in keyWords:
                        #print(reviewText_lower)
                        if w in reviewText_lower:
                            #print(reviewText_lower)
                            with open('Output.csv', 'a', newline='') as csvfile:
                                fieldnames = ['Name', 'Location', 'Stars', 'Review', 'Total', 'New Name', 'ID', 'Address New']
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                writer.writerow({'Name': name, 'Location': location, 'Stars': stars,
                                                 'Review': reviewText, 'Total': totalReviews, 'New Name': newName,
                                                 'ID': id, 'Address New': address_new})
                            scrubbedReviews += 1

                elif "title=\"2.0 star rating\"" in innerHTML:
                    reviewText = NR_Reviews[i].find_element_by_tag_name("p").text
                    #print(reviewText)
                    reviewText_lower = reviewText.lower()
                    #print(reviewText_lower)
                    stars = 2
                    #print(stars)
                    for w in keyWords:
                        if w in reviewText_lower:
                            #print(reviewText_lower)
                            with open('Output.csv', 'a', newline='') as csvfile:
                                fieldnames = ['Name', 'Location', 'Stars', 'Review', 'Total', 'New Name', 'ID']
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                writer.writerow({'Name': name, 'Location': location, 'Stars': stars,
                                                 'Review': reviewText, 'Total': totalReviews, 'New Name': newName,
                                                 'ID': id, 'Address New': address_new})
                            scrubbedReviews += 1

    return scrubbedReviews

def pageThrough():
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    pagination = driver.find_element_by_xpath("//div[@aria-label='Pagination navigation']")
    pages = pagination.find_element_by_xpath(".//span[@class=' css-e81eai']").text
    return pages


def findReviewInfo(i, keyWords, name, location, totalReviews, newName, id, address_new):
    businessReviews = driver.find_elements_by_class_name("review__373c0__13kpL")
    innerHTML = businessReviews[i].get_attribute('innerHTML')
    reviewText = businessReviews[i].find_element_by_class_name("comment__373c0__1M-px").text
    reviewText_lower = reviewText.lower()

    if "aria-label=\"1 star rating\"" in innerHTML:
        stars = 1
        for w in keyWords:
            if w in reviewText_lower:
                #print(reviewText_lower)
                with open('Output.csv', 'a', newline='') as csvfile:
                    fieldnames = ['Name', 'Location', 'Stars', 'Review', 'Total', 'New Name', 'ID', 'Address New']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'Name': name, 'Location': location, 'Stars': stars,
                                     'Review': reviewText, 'Total': totalReviews, 'New Name': newName,
                                     'ID': id, 'Address New': address_new})
                return 1

    elif "aria-label=\"2 star rating\"" in innerHTML:
        stars = 2
        for w in keyWords:
            if w in reviewText_lower:
                #print(reviewText_lower)
                with open('Output.csv', 'a', newline='') as csvfile:
                    fieldnames = ['Name', 'Location', 'Stars', 'Review', 'Total', 'New Name', 'ID', 'Address New']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'Name': name, 'Location': location, 'Stars': stars,
                                     'Review': reviewText, 'Total': totalReviews, 'New Name': newName,
                                     'ID': id, 'Address New': address_new})
                return 1

    else:
        return 0


def scrapeEachReview(name, location, pages, totalReviews, newName, id, address_new):
    lastPage = int(pages[5:])
    #print(lastPage)
    currentPage = 0
    increment = 0
    venueURL = driver.current_url
    #print(venueURL)
    totalScrubbed = 0

    while currentPage <= lastPage:
        businessReviews = driver.find_elements_by_class_name("review__373c0__13kpL")
        for i in range(len(businessReviews)):
            try:
                t = findReviewInfo(i, keyWords, name, location, totalReviews, newName, id, address_new)
                totalScrubbed += t
            except:
                try:
                    time.sleep(1)
                    findReviewInfo(i, keyWords, name, location, totalReviews, newName, id, address_new)
                except:
                    try:
                        time.sleep(5)
                        findReviewInfo(i, keyWords, name, location, totalReviews, newName, id, address_new)
                    except:
                        print("Error: Could not find comment on page {0} for {1} in {2}.Skipping to next page.".format(
                            currentPage, name, location))
                        pass

        currentPage += 1

        if currentPage == lastPage:
            break

        increment += 10
        currentURL = venueURL + "?start=" + str(increment)
        driver.get(currentURL)
        element_present = EC.presence_of_all_elements_located((By.CLASS_NAME, 'margin-t4__373c0__1TRkQ'))
        WebDriverWait(driver, timeout).until(element_present)
        element_present2 = EC.presence_of_all_elements_located((By.CLASS_NAME, 'comment__373c0__1M-px'))
        WebDriverWait(driver, timeout).until(element_present2)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    return totalScrubbed


def scrapeReviews(name, location, totalReviews, newName, id, address_new):
    try:
        pages = pageThrough()

        t = scrapeEachReview(name, location, pages, totalReviews, newName, id, address_new)
        return t
    except:
        try:
            time.sleep(1)
            pages = pageThrough()
            t = scrapeEachReview(name, location, pages, totalReviews, newName, id, address_new)
            return t
        except:
            try:
                time.sleep(5)
                pages = pageThrough()
                t = scrapeEachReview(name, location, pages, totalReviews, newName, id, address_new)
                return t
            except:
                print("Error: could not find reviews for {0} in {1}. Comment scraping skipped.".format(name, location))
                return 0


df = importData("Input.csv")

for row in range(len(df.index)):

    print("Scrubbing {0} out of {1} venues.".format((row + 1), len(df.index)))

    newName = ""
    id = ""

    address_new = ""

    try:
        newName, id, address_new = searchVenue(df['Name'][row], df['Location'][row])
    except:
        print("Could not find venue {0} in {1} in Yelp Search. Skipping Venue.".format(df['Name'][row], df['Location'][row]))
        continue
    total = scrapeReviewTotal(df['Name'][row], df['Location'][row])
    t = scrapeReviews(df['Name'][row], df['Location'][row], total, newName, id, address_new)
    #t = 0
    n = scrapeNonRecommended(df['Name'][row], df['Location'][row], id, total, newName, address_new)

    z = t + n

    if z == 0:
        with open('Output_NR.csv', 'a', newline='') as csvfile:
            fieldnames = ['Name', 'Location', 'Total', 'New Name', 'ID', 'Address New']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'Name': df['Name'][row], 'Location': df['Location'][row], 'Total': total, 'New Name': newName,
                             'ID': id, 'Address New': address_new})
