from bs4 import BeautifulSoup
import traceback
import urllib2

def get_img_link(link):
    try:
        request  = urllib2.Request(link, headers={"User-Agent" : "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13');"})
        data = urllib2.urlopen(request).read()
        soup = BeautifulSoup(data)
        images = soup.find_all("img",attrs={"id":"imgBlkFront"})
        return images[0]['src']
        
    except:
        print "ORIGINAL METHOD FAILED"
        tb = traceback.format_exc()
        print(tb)
            
test_link= "https://www.amazon.com/Fundamentals-Astrodynamics-Dover-Aeronautical-Engineering/dp/0486600610?ie=UTF8&keywords=Fundamentals%20of%20Astrodynamics&linkCode=sl1&linkId=ef930b05f0d35e3d7b4c8150e18da761&qid=1437010218&ref_=as_li_ss_tl&sr=8-1&tag=maursica-20"
print(get_img_link(test_link))
