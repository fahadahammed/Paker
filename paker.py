import os
import json
import argparse
import datetime
import time
import functools
import shutil
import markdown
from httpwatcher import HttpWatcherServer
from tornado.ioloop import IOLoop


# Variables
Project_Name = "Paker"
Version = "1.0.1"
Created_At = "2020-04-17 18:35:01.164992"
Author = "Fahad Ahammed"
Author_Email = "obak.krondon@gmail.com"
Author_Web_Page = "https://fahadahammed.github.io"
DateTime_Now = datetime.datetime.now()


def info():
    msg = {
        "Project_Name": Project_Name,
        "Version": Version,
        "Created_At": Created_At,
        "Author": Author,
        "Author_Email": Author_Email,
        "Author_Web_Page": Author_Web_Page,
        "DateTime_Now": DateTime_Now
    }
    return msg


def timeit_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # Alternatively, you can use time.process_time()
        func_return_val = func(*args, **kwargs)
        end = time.perf_counter()
        timeit_message = 'Time Took: {0:<10}.{1:<8} : {2:<8} Seconds'.format(func.__module__, func.__name__, end - start)
        # logging.warning(timeit_message)
        return func_return_val
    return wrapper


# Helper Plugin
@timeit_wrapper
def parkdown(text):
    new_lined_text = text.replace("\n", "<br>")
    return markdown.markdown(new_lined_text)


@timeit_wrapper
class FileOps:
    def __init__(self, it_is_json_file=False):
        self.it_is_json_file = it_is_json_file

    def copytree(self, src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

    def list_of_files(self, path):
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    def read_file(self, filename_with_path):
        if self.it_is_json_file:
            with open(filename_with_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(filename_with_path, 'r', encoding='utf-8') as f:
                return f.readlines()

    def read_file_without_n(self, filename_with_path):
        if self.it_is_json_file:
            with open(filename_with_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(filename_with_path, 'r', encoding='utf-8') as f:
                return f.read().splitlines()

    def write_file_without_n(self, content, filename_with_path):
        try:
            with open(filename_with_path, "a", encoding="utf-8") as f:
                f.write(content)
                return True
        except Exception as e:
            return False


# Configuration File
def site_configuration():
    return FileOps(it_is_json_file=True).read_file(filename_with_path="_Input/config.json")


class Paker:
    def __init__(self):
        self.indir = "_Input"
        self.outdir = "_Output"
        self.indirC = self.indir + "/_Contents"
        self.indirT = self.indir + "/_Theme"
        self.indirCpages = self.indirC + "/pages"
        self.indirCposts = self.indirC + "/posts"
        self.indirCstatic = self.indirC + "/static"
        self.outdirS = self.outdir + "/static"
        self.outdirP = self.outdir + "/posts"
        self.list_of_pages = FileOps().list_of_files(path=self.indirCpages)
        self.list_of_posts = FileOps().list_of_files(path=self.indirCposts)

    def copy_static(self):
        return FileOps().copytree(src=self.indirCstatic, dst=self.outdirS)

    # List to String
    def list_to_string(self, list):
        return ' '.join([str(elem) for elem in list])

    # Clear Output Directory
    def clear_output_directory(self):
        folder_path = '_Output'
        for file_object in os.listdir(folder_path):
            file_object_path = os.path.join(folder_path, file_object)
            if os.path.isfile(file_object_path) or os.path.islink(file_object_path):
                os.unlink(file_object_path)
            else:
                shutil.rmtree(file_object_path)

    # Create Directories
    def create_directories(self):
        os.mkdir("_Output/posts")
        return True

    def construct_header(self, title=None):
        if not title:
            title = site_configuration()["site_name"]
        else:
            title = title + " | " + site_configuration()["site_name"]
        head_section = FileOps().read_file_without_n(filename_with_path=self.indirT + "/head.html")
        head_section_constructed = []
        for i in head_section:
            i = i.replace("{{ title }}", title)
            i = i.replace("{{ logo-title }}", site_configuration()["site_name"])
            i = i.replace("{{ description }}", site_configuration()["description"])
            i = i.replace("{{ keywords }}", site_configuration()["keywords"])
            i = i.replace("{{ author }}", site_configuration()["author"])
            head_section_constructed.append(i)
        return head_section_constructed

    def construct_footer(self):
        to_return = []
        version_info = f'<small>Site is generated by <a href="https://github.com/fahadahammed/Paker">{Project_Name}-{Version}</a> at {str(DateTime_Now)}.</small>'
        foot_section = FileOps().read_file_without_n(filename_with_path=self.indirT + "/foot.html")
        if foot_section:
            for i in foot_section:
                if "{{ version_info }}" in i:
                    i = i.replace("{{ version_info }}", version_info)
                to_return.append(i)
        return to_return

    def construct_networks(self):
        to_return = ""
        for i in site_configuration()["networks"].keys():
            network = i.capitalize()
            name = site_configuration()["networks"][i]["name"]
            url = site_configuration()["networks"][i]["url"]
            link = f"""<li><a href="{url}"><b>{network}: </b>{name}</a></li>"""
            to_return = to_return + link
        return to_return


    def construct_menu(self):
        menu_section = FileOps().read_file_without_n(filename_with_path=self.indirT + "/menu.html")
        generated_menu = ''
        to_return = []
        if self.list_of_pages:
            for i in self.list_of_pages:
                page = FileOps().read_file_without_n(filename_with_path=self.indirCpages + "/" + i)
                title = page[0].replace("title: ", "")
                if "list" in i:
                    menu_li = '<li><a href="/posts">' + title.capitalize() + '</a></li>'
                else:
                    menu_li = '<li><a href="/' + i.split(".")[0] + '.html">' + title.capitalize() + '</a></li>'
                generated_menu = generated_menu + menu_li
        for i in menu_section:
            if "{{ menu }}" in i:
                i = i.replace("{{ menu }}", generated_menu)
            if "{{ networks }}" in i:
                i = i.replace("{{ networks }}", self.construct_networks())
            to_return.append(i)
        return to_return

    def construct_body(self, body):
        to_return = []
        menu_section = FileOps().read_file_without_n(filename_with_path=self.indirT + "/body.html")
        for i in menu_section:
            i = i.replace("{{ body }}", body)
            to_return.append(i)
        return to_return

    def generate_single_page(self, file):
        page_content = FileOps().read_file(file)
        if page_content:
            body = []
            title = page_content[0].replace("title: ", "")
            for i in page_content[2::]:
                if "List" in title:
                    if "{{ list }}" in i:
                        i = i.replace("{{ list }}", self.generate_list_of_posts())
                body.append(parkdown(text=i))
            if "index" in title:
                header_section = self.construct_header()
            else:
                header_section = self.construct_header(title=title)
            menu_section = self.construct_menu()
            body_section = self.construct_body(body=self.list_to_string(body))
            footer_section = self.construct_footer()
            full_page = header_section + menu_section + body_section + footer_section
            if full_page:
                return full_page
            else:
                return False
        else:
            return False

    def generate_all_pages(self):
        if self.list_of_pages:
            for i in self.list_of_pages:
                single_page = self.generate_single_page(file=self.indirCpages + "/" + i)
                for ii in single_page:
                    if "list" in i:
                        FileOps().write_file_without_n(content=ii,
                                                       filename_with_path=self.outdirP + "/index.html")
                    else:
                        FileOps().write_file_without_n(content=ii,
                                                       filename_with_path=self.outdir + "/" + i.split(".")[0] + ".html")
            return True
        else:
            return False

    def generate_single_post(self, file):
        post_content = FileOps().read_file(file)
        if post_content:
            body = []
            title = post_content[0].replace("title: ", "")
            dateandtime = post_content[1].replace("dateandtime: ", "")
            category = post_content[2].replace("category: ", "")
            tags = post_content[3].replace("tags: ", "")
            for i in post_content[5::]:
                body.append(parkdown(text=i))
            header_section = self.construct_header(title=title)
            menu_section = self.construct_menu()
            post_extra_info = f"""
            <div id="post_extra_info">
            <p><h1 class="post_title">{title}</h1></p>
            <div class="post_infos">
            <p><b>Created At: </b> {dateandtime} </p>
            <p><b>Category: </b> {category} <b>Tags: </b> {tags} </p>
            </div>
            </div><div id="post_body">
            """
            bodystring = self.list_to_string(body)
            body_section = self.construct_body(body=post_extra_info+bodystring+"</div>")
            footer_section = self.construct_footer()
            full_page = header_section + menu_section + body_section + footer_section
            if full_page:
                return full_page
            else:
                return False
        else:
            return False

    def generate_all_posts(self):
        if self.list_of_posts:
            for i in self.list_of_posts:
                single_post = self.generate_single_post(file=self.indirCposts + "/" + i)
                post_directory = i.split(".")[0]
                os.mkdir(self.outdirP + "/" + post_directory)
                for ii in single_post:
                    FileOps().write_file_without_n(content=ii, filename_with_path=self.outdirP + "/" + post_directory + "/index.html")
            return True
        else:
            return False

    def curated_list_of_posts(self):
        to_return = []
        if self.list_of_posts:
            for i in self.list_of_posts:
                filename = self.indirCposts + "/" + i
                title = FileOps().read_file_without_n(filename_with_path=filename)[0].replace("title: ", "")
                url = "/posts/" + i.split(".")[0]
                to_return.append({
                    "url": url,
                    "title": title
                })
        return to_return

    def generate_list_of_posts(self):
        to_return = '<div id="post_list"><ul>'
        if self.curated_list_of_posts():
            for i in self.curated_list_of_posts():
                link = f'<li><a href="{i["url"]}">{i["title"]}</a></li>'
                to_return = to_return + link
        to_return = to_return + "</ul></div>"
        return to_return


# HTTP WATCHER CUSTOM
def phttp(serving_path="_Output", watch_paths=["_Input"], host="127.0.0.1", port=9137):
    def custom_callback():
        print("File Changed, So reloading server !")
        execute()
        print(f"Server running at: https://{host}:{port}")

    server = HttpWatcherServer(
        f"{serving_path}",  # serve files from the folder /path/to/html
        watch_paths=watch_paths,  # watch these paths for changes
        on_reload=custom_callback,  # optionally specify a custom callback to be called just before the server reloads
        host=host,  # bind to host 127.0.0.1
        port=port,  # bind to port 5556
        server_base_path="/",  # serve static content from http://127.0.0.1:5556/blog/
        watcher_interval=1.0,  # maximum reload frequency (seconds)
        recursive=True,  # watch for changes in /path/to/html recursively
        open_browser=False  # automatically attempt to open a web browser (default: False for HttpWatcherServer)
    )
    server.listen()
    print(f"Server running at: https://{host}:{port}")

    try:
        # will keep serving until someone hits Ctrl+C
        IOLoop.current().start()
    except KeyboardInterrupt:
        server.shutdown()


# Execute Function
def CallPacker():
    Paker().clear_output_directory()
    Paker().create_directories()
    Paker().copy_static()
    Paker().generate_all_pages()
    Paker().generate_all_posts()


def execute():
    parser = argparse.ArgumentParser(
        description=f'{Project_Name} is a tool for creating static site from markdown files.',
        epilog=f"""{Project_Name} is a tool for creating static site from markdown files."""
    )

    # Global
    parser.add_argument('-v', '-V', '--version', action='version', version='%(prog)s {version}'.format(version=Version))

    # Create Sub Parser
    subparsers = parser.add_subparsers()

    # create the parser for the 'build' command
    parser_build = subparsers.add_parser(name="build")
    parser_build.set_defaults(parser="build")

    # create the parser for the 'run' command
    parser_run = subparsers.add_parser(name="run")
    parser_run.add_argument('--host', nargs=1, help="Give hostname",
                                 required=False)
    parser_run.add_argument('--port', nargs=1, help="Give port",
                                 required=False)
    parser_run.set_defaults(parser="run")

    # Arguments
    args = parser.parse_args()
    try:
        # Check
        if args.parser == "build":
            print("Building...")
            CallPacker()
            print("Build Complete.")
        elif args.parser == "run":
            print("Building...")
            CallPacker()
            print("Build Complete.")
            try:
                host = str(args.host[0])
                port = int(args.port[0])
                phttp(host=host, port=port)
            except Exception:
                phttp()
        else:
            pass
    except AttributeError as e:
        parser.print_usage()


if __name__ == "__main__":
    print(f"{Project_Name}-{Version} has started to work.")
    execute()
