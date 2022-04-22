import toons_ripper

# raw_link_page = toons_ripper.LinkParser("https://www.dti.link/archives/5493")
# raw_link_page = toons_ripper.LinkParser("https://www.rtilinks.com/archives/5283")
# raw_link_page = toons_ripper.LinkParser("https://www.dti.link/archives/5492")
# url = input("Enter Link:\n")
url = "https://www.rtilinks.com/archives/5770"
raw_link_page = toons_ripper.LinkManger(url)
# print(raw_link_page.link_scraper())
file = toons_ripper.FileIO(filename=raw_link_page.page_title, file_links=raw_link_page.file_links)
file.write_file()

