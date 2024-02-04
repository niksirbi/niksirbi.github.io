import pyalex

pyalex.config.email = "niko.sirbiladze@gmail.com"

# My OpenAlex ID
my_id = "A5086452643"

my_pubs = pyalex.Works().filter(
    authorships = {"author": {"id": "A5086452643"}},
    type="article",
    ).get()

print(len(my_pubs))

for pub in my_pubs:
    print(pub["title"])

