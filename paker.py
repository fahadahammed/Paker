import os
import json
import argparse
import datetime
import time
import functools
import shutil
import logging

# Variables
Project_Name = "Paker"
Version = "1.0.4"
Created_At = "2020-04-17 18:35:01.164992"
Author = "Fahad Ahammed"
Author_Email = "iamfahadahammed@gmail.com"
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
        timeit_message = '------Time Took: {0:<10}.{1:<8} : {2:<8} Seconds'.format(func.__module__, func.__name__, end - start)
        logging.warning(timeit_message)
        return func_return_val
    return wrapper


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
        try:
            result = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            return result
        except Exception:
            pass

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
        self.indirCpages = self.indirC + "/_pages"
        self.indirCposts = self.indirC + "/_posts"
        self.indirCstatic = self.indirC + "/_static"
        self.outdirS = self.outdir + "/_static"
        self.outdirP = self.outdir + "/_posts"
        self.list_of_pages = [x for x in FileOps().list_of_files(path=self.indirCpages) if "~" not in x]
        self.list_of_posts = [x for x in FileOps().list_of_files(path=self.indirCposts) if "~" not in x]

    def copy_static(self):
        try:
            shutil.copy(src=self.indirC + "/robots.txt", dst=self.outdir + "/robots.txt")
            from pathlib import Path
            Path(self.outdir + "/.nojekyll").touch()
            FileOps().copytree(src=self.indirCstatic, dst=self.outdirS)
            return True
        except Exception:
            pass

    # List to String
    def list_to_string(self, list):
        return ' '.join([str(elem) for elem in list])

    # Clear Output Directory
    def clear_output_directory(self):
        folder_path = '_Output'
        try:
            for file_object in os.listdir(folder_path):
                file_object_path = os.path.join(folder_path, file_object)
                if os.path.isfile(file_object_path) or os.path.islink(file_object_path):
                    os.unlink(file_object_path)
                else:
                    shutil.rmtree(file_object_path)
        except Exception as e:
            print(e)
            pass

    # Create Directories
    def create_directories(self):
        if not os.path.exists("_Output"):
            os.makedirs("_Output")
        if not os.path.exists("_Output/_posts"):
            os.makedirs("_Output/_posts")

    def construct_header(self, title=None):
        if title:
            title = title + " | " + site_configuration()["site_name"]
        else:
            title = site_configuration()["site_name"]
        head_section = FileOps().read_file_without_n(filename_with_path=self.indirT + "/head.html")
        head_section_constructed = []
        for i in head_section:
            i = i.replace("{{ title }}", title)
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

    def construct_menu(self):
        menu_section = FileOps().read_file_without_n(filename_with_path=self.indirT + "/menu.html")
        return menu_section

    def construct_body(self, body, post=False):
        to_return = []
        if post:
            body_section = FileOps().read_file_without_n(filename_with_path=self.indirT + "/post_body.html")
            for i in body_section:
                i = i.replace("{{ post_body }}", body)
                to_return.append(i)
        else:
            body_section = FileOps().read_file_without_n(filename_with_path=self.indirT + "/body.html")
            for i in body_section:
                i = i.replace("{{ body }}", body)
                to_return.append(i)
        return to_return

    def generate_single_page(self, file):
        body = FileOps().read_file(file)
        if body:
            new_body = []
            for i in body:
                if "{{ list }}" in i:
                    new_body.append(i.replace("{{ list }}", self.generate_list_of_posts()))
                else:
                    new_body.append(i)
        header_section = self.construct_header()
        menu_section = self.construct_menu()
        body_section = self.construct_body(body=self.list_to_string(new_body))
        footer_section = self.construct_footer()
        full_page = self.list_to_string(list=header_section) + self.list_to_string(list=menu_section) + self.list_to_string(list=body_section) + self.list_to_string(list=footer_section)
        if full_page:
            return full_page
        else:
            return False

    def generate_all_pages(self):
        if self.list_of_pages:
            for i in self.list_of_pages:
                single_page = self.generate_single_page(file=self.indirCpages + "/" + i)
                for ii in single_page:
                    if "{{ list }}" in i:
                        FileOps().write_file_without_n(content=ii,
                                                       filename_with_path=self.outdir + "/posts.html")
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
            pc = post_content[5::]
            for i in pc:
                body.append(i)
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
            body_section = self.construct_body(body=post_extra_info+bodystring+"</div>", post=True)
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
                post_directory = i.split(".")[0].lower()
                os.mkdir(self.outdir + "/" + post_directory)
                for ii in single_post:
                    FileOps().write_file_without_n(content=ii, filename_with_path=self.outdir + "/" + post_directory + "/index.html")
            return True
        else:
            return False

    def curated_list_of_posts(self):
        to_return = []
        if self.list_of_posts:
            for i in self.list_of_posts:
                filename = self.indirCposts + "/" + i
                title = FileOps().read_file_without_n(filename_with_path=filename)[0].replace("title: ", "")

                dateandtime = FileOps().read_file_without_n(filename_with_path=filename)[1].replace("dateandtime: ", "")
                category = FileOps().read_file_without_n(filename_with_path=filename)[2].replace("category: ", "")
                url = "/" + i.split(".")[0]
                to_return.append({
                    "url": url,
                    "title": title,
                    "dateandtime": dateandtime,
                    "category": category
                })
        return to_return

    def generate_list_of_posts(self):
        to_return = '<div id="post_list"><ul>'
        if self.curated_list_of_posts():
            for i in self.curated_list_of_posts():
                sub_link = f'<div><small><strong>Date&Time: </strong>{i["dateandtime"]}, <strong>Category: </strong>{i["category"]}</small></div>'
                link = f'<li><h2><a href="{i["url"]}">{i["title"]}</a></h2>{sub_link}</li>'
                to_return = to_return + link
        to_return = to_return + "</ul></div>"
        return to_return


@timeit_wrapper
def execute():
    Paker().clear_output_directory()
    Paker().create_directories()
    Paker().copy_static()
    Paker().generate_all_pages()
    Paker().generate_all_posts()


if __name__ == "__main__":
    print(f"{Project_Name}-{Version} has started to work.")
    execute()