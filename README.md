# Paker
Paker stands for "Page+Maker". The purpose of this project is 
to give a tool which will transform markdown to html static.

## Structure
The input directory structure is as follows:

```bash
_Input/
├── config.json
├── _Contents
│   ├── pages
│   │   ├── index.md
│   │   └── list.md
│   ├── posts
│   │   ├── my-first-post.md
│   │   └── my-second-post.md
│   ├── robots.txt
│   └── static
│       ├── css
│       │   └── styles.css
│       └── img
│           ├── border.png
│           └── favicon.ico
└── _Theme
    ├── body.html
    ├── foot.html
    ├── head.html
    └── menu.html

7 directories, 13 files
```
In root of input directory, a config.json file is expected.

```json
{
  "site_name": "Fahads Realm",
  "description": "A quest to put the dreams into words.",
  "keywords": "Journey, Technology, Hobby",
  "author": "Fahad Ahammed",
  "email": "iamfahadahammed@gmail.com",
  "networks": {
    "twitter": {
      "url": "https://twitter.com/obakfahad",
      "name": "obakfahad"
    },
    "linkedin": {
      "url": "https://www.linkedin.com/in/fahadahammed",
      "name": "fahadahammed"
    },
    "github": {
      "url": "https://github.com/fahadahammed",
      "name": "fahadahammed"
    }
  },
  "domain": "https://fahadahammed.com"
}
```

And then, there are two folders:

1. _Contents
2. _Themes

Themes folder is all about static structure of the site and the Contents folder is about the posts and pages.


## How to

To build the pages from **_Input** directory:
```bash
./paker
```

To build the pages from **_Input** directory and serve the pages for testing the chages:
```bash
./paker run
```