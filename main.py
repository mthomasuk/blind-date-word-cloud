import re
import requests
import tqdm
import matplotlib.pyplot as plt

from pyquery import PyQuery as pq
from wordcloud import WordCloud

class bcolours:
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def dedupe(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def main():

    text = ""
    first_link = ""

    for x in tqdm.tqdm(range(50)):

        r = requests.get('https://www.theguardian.com/lifeandstyle/series/blind-date?page=' + str(x + 1))

        status_code = r.status_code

        if status_code == 200:
            d = pq(r.text)

            links = d('a[data-link-name="article"]')
            links = [pq(a).attr("href") for a in links]

            for i, a in enumerate(dedupe(links)):
                if i == 0 and x == 0:
                    first_link = a
                elif a == first_link:
                    break

                try:
                    p = requests.get(a)

                    if p.status_code == 200:
                        html = pq(p.text)

                        p_tags = html('div[data-test-id="article-review-body"]').find('p')
                        text_i_want = pq(p_tags).text()

                        regexr = re.compile("(Describe .* in three words\n)(.*\.)")
                        captured = regexr.search(text_i_want)

                        try:
                            text = text + captured.group(2).lower() + "\n"
                        except Exception:
                            pass


                except Exception as e:
                    print(bcolours.FAIL + "\n" + a + "\n" + bcolours.ENDC)
                    pass

        else:
            print("ERROR")
            print(status_code)
            break;

    wordcloud = WordCloud(margin=10, random_state=1).generate(text)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()
    wordcloud.to_file("./cloudy-with-a-chance-of-asinine-observations.png")

if __name__ == "__main__":
    main()
