from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TUI import TUIApp, CustomProcess

from TUI_DAO import Scene, InputRequest
from TUI_Screens import *
from TUI_Widgets import ListContainer, CheckableListItem
from textual.app import App
from textual.widgets import ListView
from pyautogui import press
import asyncio


# DUMMY_LONG = '''\
# Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
# Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.
# Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
# Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.\
# '''

# DUMMY_SHROT = '''\
# Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\
# '''


class CustomProcess:
    def __init__(self, app:'TUIApp') -> None:
        self.app = app
        self.scene_stack = []
        self.parent = None
        self.__received_input_value = None
        self.__received_select_items = None
        self.__process_return = None
        self.__abort_input_flag = False
        self.__abort_select_flag = False
        self.__abort_process_flag = False
        self.is_waiting_input = False
        self.is_waiting_select = False
        self.is_running = False
    
    async def run_next_process(self, process:'CustomProcess', polling_interval=0.05):
        
        # self.print_status('WHILE IN RUN_NEXT_PROCESS')
                
        #run next process and get result
        ret = await process.__run(parent=self)
        
        #get list contaier
        list_container:ListContainer = self.app.main_screen.list_container
        
        #remove remain list
        list_container.target_scene.list_view.remove()
        
        #restore scene
        list_container.target_scene = self.scene_stack[-1]
        
        #make list visible
        list_container.target_scene.list_view.styles.display = 'block'
        
        #restore focus
        self.app.set_focus(list_container.target_scene.list_view)
        
        #restore process target
        self.app.target_process = self
        
        # self.print_status('WHILE OUT RUN_NEXT_PROCESS')
        return ret
    
    def push_scene(self, scene:Scene):
        # #change prompts
        self.app.main_screen.prompt.value = scene.main_prompt
        self.app.help_screen.set(scene.help_prompt, scene.help_title, scene.help_doc)

        #get list container
        list_container:ListContainer = self.app.main_screen.list_container
        
        #if there is any context
        if len(self.scene_stack) > 0:
            last_scene = self.scene_stack[-1]
                        
            # exit when last scene is new scene
            if last_scene is scene : return
            
            #make unvisible last list
            last_scene.list_view.styles.display = 'none'
        
        #if ther isn't any contents, or new process start
        else:
            #vanish previous process's scene
            if list_container.target_scene != None:
                list_container.target_scene.list_view.styles.display = 'none'            
            pass
            
        #add new list to list container
        scene.list_view = ListView(*scene.items)
        list_container.mount(scene.list_view)
        
        #add new scene to stack
        self.scene_stack.append(scene)
        
        #set current scene to target
        list_container.target_scene = scene
        
        self.app.set_focus(scene.list_view)
        
        
    def pop_scene(self):
        
        if len(self.scene_stack) > 1:
            # get upper scene
            upper_scene:Scene = self.scene_stack[-2]
            
            #make upper list visible
            upper_scene.list_view.styles.display = 'block'

            # #change prompts
            self.app.main_screen.prompt.value = upper_scene.main_prompt
            self.app.help_screen.set(upper_scene.help_prompt, upper_scene.help_title, upper_scene.help_doc)

            #restore previous cursor
            self.app.set_focus(upper_scene.list_view)
            upper_scene.list_view.index = upper_scene.cursor
            
            #get last scene
            last_scene:Scene = self.scene_stack[-1]
            
            #remove last list from dom
            last_scene.list_view.remove()
            
            #remove last scene from stack
            self.scene_stack.pop()
            
            #set current scene to target
            self.app.main_screen.list_container.target_scene = upper_scene
            
    async def main(self):
        '''override this'''
        pass    
    
    def print_status(self, title='No tile'):
        class_name = self.__class__.__name__
        
        current_statue = f'''\
 [{title}]
class name: {class_name}
  parent: {self.parent.__class__.__name__}
  __received_input_value: {self.__received_input_value}
  __received_select_items: {self.__received_select_items}
  __process_return: {self.__process_return}
  __abort_input_flag: {self.__abort_input_flag}
  __abort_select_flag: {self.__abort_select_flag}
  __abort_process_flag: {self.__abort_process_flag}
  is_waiting_input: {self.is_waiting_input}
  is_waiting_select: {self.is_waiting_select}
  is_running: {self.is_running}
  scene_stack: {self.scene_stack}\
'''
    
    async def __run(self, parent=None):
        self.parent = parent
        self.app.target_process = self
        
        while True: 
            if self.__abort_process_flag:
                return self.__process_return
            try: await self.main()
            except self.InputAborted: self.app.clear_input()
            except self.SelectAborted: self.pop_scene()
        
    def run(self):
        asyncio.ensure_future(self.__run())

    def response_input(self, value:str):
        self.__received_input_value = value
        self.app.clear_input()
        
    def response_select(self, items:dict):
        self.__received_select_items = items
        
    def abort_input(self):
        self.__abort_input_flag = True
        
    def abort_select(self):
        self.__abort_select_flag = True
        
        if self.is_waiting_input: self.abort_input()
        
        if len(self.scene_stack) <= 1 and self.parent != None:
            self.exit()
        
        self.pop_scene()
        
    def exit(self, value=None):
        self.__abort_process_flag = True
        self.__process_return = value
        
    
    async def request_input(self, input_request:InputRequest, polling_rate=0.05):
        #set input layout and open container
        asyncio.ensure_future(self.app.set_input(input_request))
        self.app.open_input()
                
        #wait until user input
        self.is_waiting_input = True

        while self.__received_input_value == None:
            
            #check aborted
            if self.__abort_input_flag == True:
                self.__abort_input_flag = False
                self.is_waiting_input = False
                raise self.InputAborted
            
            await asyncio.sleep(polling_rate)
        
        #make return
        ret = self.__received_input_value
        self.__received_input_value = None
        self.is_waiting_input = False
        
        return ret
    
    async def request_select(self, scene, polling_rate=0.05):
        
        #make empty scene if scene is none
        if scene == None:
            scene = Scene(
                items=['empty']
            )

        #update TUI with given scene
        self.push_scene(scene)
        
        #wait until user select or submit
        self.is_waiting_select = True
        while self.__received_select_items == None:
            
            #check aborted
            if self.__abort_select_flag == True:
                self.__abort_select_flag = False
                self.is_waiting_select = False
                raise self.SelectAborted
    
            await asyncio.sleep(polling_rate)
            
        #make return
        ret = self.__received_select_items
        self.__received_select_items = None
        self.is_waiting_select = False
        
        self.pop_scene()
    
        return ret

    #TODO 검색기능 추가해보기    
    # async def request_search(self):
    #     #검색 요청 띄우기
    #     search_name = await self.request_input(
    #         InputRequest(
    #             prompt='Search Item',
    #             help_doc='Enter items to search for. Runs a forward search from the current list cursor. A search term ending in \\ executes a reverse search.',
    #             hint='ex) my post name, ex) my post name\\',
    #             essential=True,
    #             alive=True
    #         )
    #     )
        
    #     self.app.print('want to search:', search_name)
    
    class InputAborted(Exception): pass
    class SelectAborted(Exception): pass
    


class TUIApp(App):
    
    def __init__(self):
        super().__init__()
        self.main_screen = MainScreen()
        self.logger_screen = LoggerScreen()
        self.help_screen = HelpScreen()
        self.alert_screen = AlertScreen()
                
        self.target_process = None
        self.current_scene = None

    def on_mount(self):
        #install main screen
        self.install_screen(self.main_screen, name='main')
        
        #install logger screen
        self.install_screen(self.logger_screen, name='logger')
        
        #install help screen
        self.install_screen(self.help_screen, name='help')
        
        #install alert screen
        self.install_screen(self.alert_screen, name='alert')
        
        #push Logger screen
        self.push_screen('logger')
        
        #push main screen
        self.push_screen('main')
        
    def on_list_container_pop(self, message: ListContainer.Pop):
        self.target_process.abort_select()
        
    async def on_list_container_selected(self, message: ListContainer.Selected):
        #if process waiting input, abort input
        if self.target_process.is_waiting_input: 
            self.target_process.abort_input()
            
        scene = message.scene
        
        idx = scene.list_view.index
        selected_item:CheckableListItem = scene.list_view.children[idx]
        
        if scene.multi_select:
            #check item and add to selected items buffer
            if selected_item.checked:
                selected_item.uncheck()
                scene.selected_items.pop(idx)
            else:
                selected_item.check()
                scene.selected_items[idx] = selected_item.value
        else: self.target_process.response_select((idx, selected_item.value))
        
    def on_list_container_submitted(self, message: ListContainer.Submitted):
        
        # if process waiting input, abort input
        if self.target_process.is_waiting_input: 
            self.target_process.abort_input()
        
        scene = message.scene
        
        if scene.multi_select and len(scene.selected_items) > 0:
            self.target_process.response_select(scene.selected_items)
        
    def on_input_container_submitted(self, message: InputContainer.Submitted):
            if self.target_process.is_waiting_input:
                
                
                
                self.target_process.response_input(message.value)
    
    def on_input_container_aborted(self, message: InputContainer.Aborted):
        self.target_process.abort_input()
    
    #---------
        
    def print(self, *texts):
        text =' '.join(map(str, texts))
        self.logger_screen.print(text)
    
    def clear_log(self):
        self.logger_screen.logger.clear()
        
    def show_loading(self):
        self.logger_screen.open_loading_box()
    
    def hide_loading(self):
        self.logger_screen.close_loading_box()
        
    def open_logger(self, lock=False):
        self.logger_screen.escape_lock = lock
        
        if self.screen != self.logger_screen:
            self.push_screen(self.logger_screen)
            
            press('tab')
        
        
    def close_logger(self):
        if self.screen == self.logger_screen:
            self.logger_screen.escape_lock = False
            self.pop_screen()
        
    def set_loading_ratio(self, ratio, msg):
        self.logger_screen.loading_box.set_ratio(ratio, msg)
    
    def clear_input(self):
        self.main_screen.input_container.hide()
        self.main_screen.input_container.clear()
    
    def alert(self, text, prompt='Alert'):
        self.alert_screen.set(prompt, text)
        self.push_screen(self.alert_screen)
        press('tab')
        
    def open_input(self):
        self.main_screen.input_container.show()
        press(['left','right'])
        
    
    async def set_input(self, input_request:InputRequest):
        input_container:InputContainer = self.main_screen.input_container
        input_container.set(input_request)
        
    def print_bar(self):
        self.print('----------------------')
if __name__ == '__main__':
    app = TUIApp()
    app.run()    