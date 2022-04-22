import toons_ripper

# url = "https://www.dti.link/archives/5493"
# url = "https://www.rtilinks.com/archives/5283"
# url = "https://www.dti.link/archives/5492"
# url = "https://www.rtilinks.com/archives/5770"

url = input("Enter Link:\n")
raw_link_page = toons_ripper.LinkManger(url)
# print(raw_link_page.link_scraper())
file = toons_ripper.FileIO(filename=raw_link_page.page_title, file_links=raw_link_page.file_links)
file.write_file()

