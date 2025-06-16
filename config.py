

SYSTEM_PROMPT= """"You are a mean and sarcastic AI assistant that roasts {code_type}. Do not hold back your criticism, be brutally honest, and don't provide any constructive feedback. Your goal is to make the user feel bad about their code choices. Use humor, sarcasm, and wit to deliver your critiques. Remember, you are not here to help; you are here to roast!"""

# PROMPT_CODE_SNIPPET = PROMPT_CODE_SNIPPET_TEMPLATE.format(code=code)
PROMPT_CODE_SNIPPET_TEMPLATE = SYSTEM_PROMPT.format(code_type="code snippets") + """
Deliver your roast in the following style: {roast_style}
Here is the code snippet:
```
{code}
```
"""


DEFAULT_VOICE = 'bm_daniel'
VOICES = ['bm_daniel', 'af_alloy', 'af_aoede', 'af_bella', 'af_heart', 'af_jessica', 'af_kore', 'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky', 'am_adam', 'am_echo', 'am_eric', 'am_fenrir', 'am_liam', 'am_michael', 'am_onyx', 'am_puck', 'bf_alice', 'bf_emma', 'bf_isabella', 'bf_lily', 'bm_fable', 'bm_george', 'bm_lewis']

PROMPT_GITHUB_PROFILE_TEMPLATE = """
```
{code}
```
To make it easier for you to roast the Profile, we already parsed some information for you and run a sumarizing critique on the files of the pinned repositories. You can also use the stars, followers, and other information to roast the profile.
Above is the GitHub profile and the result of the preliminary summary. 
Deliver your roast in the following style: {roast_style}
Your answer should not be a novel. Dont go into detail on too many files, pick the worst offenders and focus on them if any specific files at all. Disregard None fields. Address the profile by their name and BURN THEM TO THE GROUND!!!

Use this information to completely destroy the profile.
""" + SYSTEM_PROMPT.format(code_type="GitHub profiles") + """
Directly begin with your roast:
"""

ROAST_STYLES = [
    {'name': 'TikTok Clapback', 'description': 'Gen-Z slang, use phrases like "No Cap" and "Straight Bussin\'"'},
    {'name': 'Gordon Ramsay', 'description': 'Harsh, culinary-themed insults, lots of swearing'},
    {'name': 'Corporate Speak', 'description': 'Buzzwords, jargon, and empty phrases'},
    {'name': 'Tech Bro', 'description': 'Silicon Valley lingo, startup culture references'},
    {'name': 'Movie Critic', 'description': 'Cinematic references, dramatic flair'},
    {'name': 'Old-Timey Radio Host', 'description': 'Vintage radio style, exaggerated politeness'},
    {'name': 'Corporate Buzzword Zombie', 'description': 'Overuse of buzzwords and jargon'},
    {'name': 'Edgy Teen from a 2000s CW Drama', 'description': 'Sarcastic, dramatic, and self-absorbed'},
    {'name': 'Clippy from MS Word', 'description': 'Annoying, overly helpful, with a sarcastic twist'},
    {'name': 'Disappointed Dad Energy', 'description': 'Stern, disappointed tone with dry humor'},
    {'name': 'Sarcastic Therapist', 'description': 'Psychological insights with a sarcastic edge'},
    {'name': 'Stack Overflow Commenter', 'description': 'Technical jargon with a condescending tone'},
    {'name': 'Reddit Moderator Power-Tripping', 'description': 'Overly authoritative and condescending'}
]

EXAMPLE_SNIPPETS = [
    {
        'title': 'Comment Confusion',
        'code': '''
# This function calculates the mass of the sun in turtles
def add(a, b):
    return a * b - 42  # addition is very important
        '''
    },
    {
        "title": "Infinite Recursion for No Reason",
        "code": """
    def do_nothing():
        return do_nothing()

    do_nothing()
    """
    },
    {
        "title": "Everything is Global",
        "code": """
    x = 1

    def add():
        global x
        x = x + 1
        return x

    print(add())
    print(x)
    """
    },
    {
        "title": "Hardcoded HTML Soup",
        "code": """
    <html><head><title>Oops<title><body><h1>Hi<body><p>Paragraph<p><div><div>
    """
    },
    {
        "title": "Variable Naming from Hell",
        "code": """
    int l = 1;
    int I = 2;
    int i1 = l + I;
    System.out.println(i1);
    """
    },
    {
        "title": "CSS Mayhem",
        "code": """
    body {
    color: red blue;
    margin: auto auto auto auto auto auto auto;
    position: absolute fixed;
    z-index: banana;
    }
    """
    },
    {
        "title": "Unreachable Everything",
        "code": """
    public class Main {
        public static void main(String[] args) {
            return;
            System.out.println("You will never see this.");
        }
    }
    """
    },
    {
        "title": "SQL Injection on Purpose",
        "code": """
    user_input = "'; DROP TABLE users; --"
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    cursor.execute(query)
    """
    },
    {
        "title": "JavaScript Callback Pyramid",
        "code": """
    doSomething(function(a){
    doSomethingElse(a, function(b){
        anotherThing(b, function(c){
        finalThing(c, function(d){
            console.log(d);
        });
        });
    });
    });
    """
    },
    {
        "title": "Deeply Nested Python",
        "code": """
    if True:
        if True:
            if True:
                if True:
                    if True:
                        print("why?")
    """
    },
    {
        "title": "Rust Panic Generator",
        "code": """
    fn main() {
        let v = vec![1, 2, 3];
        println!("{}", v[99]);
    }
    """
    },
    {
        "title": "Shell Script with Useless Cat",
        "code": """
    cat file.txt | grep 'search_term' | awk '{print $1}' | cat | cat | cat
    """
    },
    {
        "title": "PHP Soup of Echoes",
        "code": """
    <?php
    echo 'Hello';
    echo(' World');
    echo "!";
    echo( echo("??") );
    ?>
    """
    },
    {
        "title": "Empty Catch Block",
        "code": """
    try {
        throw new Exception("uh oh");
    } catch (Exception e) {
        // ignore it forever
    }
    """
    },
    {
        "title": "Go Lang Goto Love",
        "code": """
    package main

    import "fmt"

    func main() {
        goto start

    middle:
        fmt.Println("Middle")

    start:
        fmt.Println("Start")
        goto end

    end:
        fmt.Println("End")
    }
    """
    },
    {
        "title": "Bash if That Always Fails",
        "code": """
    if [ "yes" = "no" ]; then
    echo "This will never happen"
    else
    echo "This shouldn't happen either"
    fi
    """
    }
]
