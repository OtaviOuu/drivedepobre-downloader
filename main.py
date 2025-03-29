import asyncio
import aiohttp
import aiofiles
from parsel.selector import Selector
from pathlib import Path
from tqdm import tqdm
import os


async def download_pdf(session, pdf_url):
    async with session.get(pdf_url) as res:
        html = await res.text()
        doc = Selector(text=html)
        pdf_src = doc.css("embed::attr(src)").get()

        hidden_path = doc.css("ul.dropdown-menu li a::text").getall()
        visible_path = doc.css(".breadcrumb-item a::text").getall()
        paths = visible_path + hidden_path

        path_string = "/".join(paths)

        path = Path(path_string.replace("...", "main"))
        async with session.get(pdf_src) as pdf_res:
            async with aiofiles.open(path, "wb") as f:
                await f.write(await pdf_res.read())


async def download_mp4(session, mp4_url):
    async with session.get(mp4_url) as res:
        html = await res.text()
        doc = Selector(text=html)
        mp4_src = doc.css("#player source::attr(src)").get()

        hidden_path = doc.css("ul.dropdown-menu li a::text").getall()
        visible_path = doc.css(".breadcrumb-item a::text").getall()
        paths = visible_path + hidden_path

        path_string = "/".join(paths)
        path = Path(path_string.replace("...", "comeco"))
        os.makedirs(path.parent, exist_ok=True)
        return
        async with session.get(mp4_src) as mp4_res:
            async with aiofiles.open(path, "wb") as f:
                await f.write(await mp4_res.read())


async def download_folder(folder_url, deep):
    async with aiohttp.ClientSession() as session:
        async with session.get(folder_url) as res:
            html = await res.text()
            doc = Selector(text=html)

            if deep == 0:
                main_folder_name = doc.css(".breadcrumb-item")[-1].css("a::text").get()
                print(
                    main_folder_name.replace(" ", "_")
                    .replace(":", "_")
                    .replace("?", "_")
                    .replace("&", "_")
                )
                deep += 1
            rows = doc.css("#file-list tr")
            for file in tqdm(
                rows, desc=f"Downloading {folder_url}", unit="file", total=len(rows)
            ):
                file_type = file.css("a span::text").get()
                file_href = f"https://drivedepobre.com{file.css('a::attr(href)').get()}"
                file_name = file.css("a::text").get()

                match file_type:
                    case "folder":
                        await download_folder(file_href, deep)
                        continue
                    case "picture_as_pdf":
                        await download_pdf(session, file_href)
                        continue
                    case "movie":
                        await download_mp4(session, file_href)
                        continue
                    case _:
                        print("Unknown file type:", file_type)
                        print("File href:", file_href)
                        print("File name:", file_name)
                        continue


async def main():
    await download_folder("https://drivedepobre.com/pasta/015bd0db68", 0)


if __name__ == "__main__":
    asyncio.run(main())
