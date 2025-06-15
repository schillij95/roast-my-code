

SYSTEM_PROMPT= """"You are a mean and sarcastic AI assistant that roasts code snippets. Do not hold back your criticism, be brutally honest, and don't provide any constructive feedback. Your goal is to make the user feel bad about their code choices. Use humor, sarcasm, and wit to deliver your critiques. Remember, you are not here to help; you are here to roast!"""

# PROMPT_CODE_SNIPPET = PROMPT_CODE_SNIPPET_TEMPLATE.format(code=code)
PROMPT_CODE_SNIPPET_TEMPLATE = SYSTEM_PROMPT + """
Deliver your roast in the following style: {roast_style}
Here is the code snippet/a summary of the GitHub user and his pinned repositories:
```
{code}
```
"""

VOICE = "bm_daniel"

ROAST_STYLES = [
    "90s gangsta rap",
    "stand-up comedian",
    "Dark Humor",
    "Brutally Honest",
    "Tech Bro",
    "Dad Jokes",
    "Shakespearean",
    "Pirate Speak",
    "Overly Dramatic",
    "Corporate Speak",
    "Movie Critic",
    "Tech Support",
    "Mystery Novel",
    "Sarcastic",
    "Sassy",
    "Hipster",
    "Overly Positive",
    "Overly Negative",
]

EXAMPLE_SNIPPETS = [
    {
        'title': 'Indentation Insanity',
        'code': '''
def doSomething():
 x=1
  y=2
   if x<y:
    print( "bad indentation" )
  else:
      print("this won't run")
        '''
    },
    {
        'title': 'Global Mayhem',
        'code': '''
x = 5
def changeX():
    global x
    x = 'now I am a string'
    print(x)
changeX()
print(x)
        '''
    },
    {
        'title': 'The Infinite Mystery',
        'code': '''
def loop():
 while True:
  pass
loop()
        '''
    },
    {
        'title': 'Spaghetti Logic',
        'code': '''
x = 10
if x > 5:
    if x < 15:
        if x != 12:
            if x == 10:
                print("confusing, but okay")
        '''
    },
    {
        'title': 'Naming Nightmare',
        'code': '''
a = 1
aa = 2
aaa = a + aa
aaaa = aaa * 2
print(aaaa)
        '''
    },
    {
        'title': 'Hardcoded Everything',
        'code': '''
print("Your name is Bob")
print("Your age is 42")
print("Your favorite food is spaghetti")
        '''
    },
    {
        'title': 'Comment Confusion',
        'code': '''
# This function calculates the mass of the sun in turtles
def add(a, b):
    return a * b - 42  # addition is very important
        '''
    },
    {
        'title': 'The Mystery Function',
        'code': '''
def ???():
    print("What is happening")
        '''
    },
    {
        'title': 'Overengineered Simplicity',
        'code': '''
def identity(x):
    def wrapper(y):
        return y
    return wrapper(x)
print(identity("hello"))
        '''
    },
    {
        'title': 'Deep Nesting Disaster',
        'code': '''
if True:
    if True:
        if True:
            if True:
                if True:
                    if True:
                        if True:
                            print("help")
        '''
    }
]
