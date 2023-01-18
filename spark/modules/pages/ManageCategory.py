import sys
sys.path.append('./spark/modules/')
sys.path.append('./spark/modules/pages/')

from TUI import *
from TUI_DAO import *

import shutil
import os

from pages import ManagePost

class ManageCategoryProcess(CustomProcess):
    def __init__(self, app: 'TUIApp') -> None:
        super().__init__(app)
        
        self.funcs = [
            self.create_category,
            self.rename_category,
            self.delete_category,
            self.change_category
        ]
        
        func_names = get_func_names(self.funcs)
        
        self.scene = Scene(
            main_prompt='Manage Category',
            items=func_names
        )
        
    async def main(self):
        idx, val = await self.request_select(self.scene)
        await self.funcs[idx]()
        
    
    async def create_category(self):
        await create_category(self, self.app)
    
    async def rename_category(self):
        await asyncio.create_task(rename_category(self, self.app))
        pass
    
    async def delete_category(self):
        # self.app.push_scene(get_category_select_scene(
        # prompt='Which category do you want to delete?'))
    
        # dup_list = [child.str for child in self.app.contents_listview.children]
    
        # idx, item = self.app.get_selected_items()
        # spark.app.alert(f'selected: {idx}, {dup_list[idx]}')
        
        # spark.remove_list_item(idx)
        # dup_list = dup_list[:idx] + dup_list[min(len(dup_list) - 1, idx + 1):]
        pass
    
    async def change_category(self):
        #filepath 변수 선언하기
        
        # f = open(filepath, 'r', encoding='utf-8')
        # raw = f.read()
        # f.close()
        # raw = raw.replace('categories: [category1]', 'categories: [%s]' % category_name, 1)
        
        # f = open(filepath, 'w', encoding='utf-8')
        # f.write(raw)
        # f.close()
        pass



#-------------------------------------------------------------


async def create_category(process:CustomProcess, app:TUIApp):
    category_name = await process.request_input(
        InputRequest(
            prompt='Type your new category name.',
            hint='new category name',
            essential=True
        )
    )
    
    build_category_md(category_name)
    os.makedirs(f'./_posts/{category_name}', exist_ok=True)
    app.alert(f'Successfully created new category:{category_name}.')
    

async def rename_category(process:CustomProcess, app:TUIApp):
    #카테고리 이름을 변경하고 카테고리 내부 포스트에도 변경사항 반영
    
    #카테고리 입력받기
    category_scene = get_category_select_scene('Rename Category')
    
    if category_scene == None: 
        app.alert('You have not created any categories yet.', 'Error')
        return
    
    #카테고리 이름 가져오기
    _, category_name = await process.request_select(category_scene)
    
    #새 카테고리 이름 입력받기
    new_category_name = await process.request_input(
        InputRequest(
            prompt=f'Rename category {category_name}',
            help_doc='Please enter a new category name',
            hint='new category name',
            essential=True,
            prevalue=category_name
        )
    )
    
    #새 카테고리가 이미 있는지 확인하기
    category_list = os.listdir('./_posts/')
    
    if new_category_name in category_list:
        app.alert(f'Category {new_category_name} already exists.', 'Error')
        
    #새 카테고리 md 만들기
    build_category_md(new_category_name)
    
    #이전 카테고리 md 지우기
    os.remove(f'./category/{category_name}.md')
    
    #포스팅 목록 가져오기
    post_list = os.listdir('./_posts/' + category_name)
    
    app.print(f'[* Rename Category]')
    
    #모든 포스트 순회
    app.open_logger(lock=False)
    app.show_loading()
    loading_i, loading_total = 0, len(post_list)
    for post_name in post_list:
        app.set_loading_ratio(loading_i / loading_total, msg=f'updating category of {post_name}')
        loading_i += 1
        await asyncio.sleep(0.001)
        
        #포스팅 경로 만들기
        post_path = f'./_posts/{category_name}/{post_name}/{post_name}.md'
        
        #포스팅 파일 열기
        f = open(post_path, 'r', encoding='utf-8')
        f_raw = f.read()
        f.close()
        
        #포스팅 categories 수정
        f_raw = f_raw.replace(f'categories: [{category_name}]', f'categories: [{new_category_name}]', 1)
        
        #파일 쓰기
        app.print(f"  Updating post's category: {post_path}")
        f = open(post_path, 'w', encoding='utf-8')
        f.write(f_raw)
        f.close()
        
    #카테고리 폴더 이름 변경
    app.print('  Moving category dir to new one')
    shutil.move(f'./_posts/{category_name}', f'./_posts/{new_category_name}')
       
    app.hide_loading()
    app.print(f'[* Rename Category Done]')
    app.alert(f'Successfully renamed category {category_name} to {new_category_name}.')
    app.close_logger()

async def delete_category(process:CustomProcess, app:TUIApp): 
    category_scene = get_category_select_scene('Rename Category')
    
    if category_scene == None: 
        app.alert('You have not created any categories yet.', 'Error')
        return
    
    #카테고리 이름 가져오기
    _, category_name = await process.request_select(category_scene)
    
    #내부 포스팅 다 지울지 물어보기
    want_remove_all = await process.request_input(
        InputRequest (
            prompt=f'Do you want to remove all posts in the category {category_name}?',
            help_doc='Default is no. If you answer as selected category name, clear all posts, If not move them to the uncategorized folder.',
            hint=f'{category_name} or any',
        )
    )
    
    want_remove_all = True if want_remove_all == category_name else False
    
    #카테고리 md 삭제
    os.remove(f'./category/{category_name}.md')
    
    

async def change_category(process:CustomProcess, app:TUIApp): pass

#--------------------------------------------------------------------------

def get_category_select_scene(prompt, multi_select=False):
    category_dir_path = './category'
    os.makedirs(category_dir_path, exist_ok=True)

    category_list = os.listdir(category_dir_path)

    categories = [filename.split('.')[0] for filename in category_list]

    try: categories.remove('uncategorized')
    except ValueError: build_category_md('uncategorized')
    
    #check if there is no category
    scene = Scene(
        main_prompt=f'{prompt} - Select Category',
        items=categories,
        multi_select=multi_select
    ) if len(categories) > 0 else None

    return scene

def build_category_md(category_name):
    f = open(f'./category/{category_name}.md', 'w')
    f.write(f'---\nlayout: category\ntitle: {category_name}\n---\n')
    f.close()