
import textwrap
import pygame
import os

class Config(object):
    """ A utility for configuration """
    def __init__(self, options, *look_for):
        assertions = []
        for key in look_for:
            if key[0] in list(options.keys()): exec('self.'+key[0]+' = options[\''+key[0]+'\']')
            else: exec('self.'+key[0]+' = '+key[1])
            assertions.append(key[0])
        for key in list(options.keys()):
            if key not in assertions: raise ConfigError(key+' not expected as option')

class text_box(object):
    def __init__(self,**kwargs):
        self.options = Config(kwargs,
                              ['rect','pygame.Rect((0,0),(0,0))'],
                              ['font', 'pygame.font.Font(os.path.join(os.getcwd(),"data","fonts","freesansbold.ttf"), 12)'],
                              ['color', '(0,0,0)'],
                              ['max_lines', '-1'],
                              ['max_lines_mode', '"last_lines"'],#how to cut the lines, save the top $number or last $number
                              ['text', '"default text"'],
                              ['indent','""']
                             )
        self.debug = False
        self.__old_rect = self.options.rect
        
        self.textwraper=textwrap.TextWrapper()
        self.textwraper.initial_indent=''
        
        self.render()
    def render(self):
        self.textwraper.initial_indent=self.options.indent
        txt=[]
        line_num=0#what line we are on for the final output
        #split the text across new lines
        for index,text in enumerate(self.options.text.split('\n')):
            if len(text)==0:
                #our text is '', so skip it,
                ##TODO:: make this add a blank line
                temp_var=self.options.font.render(text,True,self.options.color).convert_alpha()
                #get the rect, we have to position it...
                rect=temp_var.get_rect()
                topleft=self.options.rect.topleft
                #set topleft postion
                topleft=(topleft[0],topleft[1]+(rect.height*line_num))
                rect.topleft=topleft
                line_num+=1
                #add to our list the current txt line...
                txt.append((temp_var,rect))
                
                continue
            #average letter size?
            let_size=(float(self.options.font.size(text)[0])/float(len(text)))
        
            #how big is our box?
            box_size=float(self.options.rect.width)
        
            #after how many letters must we wrap the line?
            wrap=box_size/let_size
        
            if self.debug==True:
                #print way too much info:letters per line (lpl), box width, and average letter size...
                print(('main::txt_box_render::lpl:%s   box_size:%s   letsize:%s\n>>>"%s"'%(wrap,box_size,let_size,text)))
            #use the textwrap modual (yay for bateries included...)
            self.textwraper.width=int(wrap)
            for num,line in enumerate(self.textwraper.wrap(text)):
                #render a line of text
                temp_var=self.options.font.render(line,True,self.options.color).convert_alpha()
                #get the rect, we have to position it...
                rect=temp_var.get_rect()
                topleft=self.options.rect.topleft
                #set topleft postion
                topleft=(topleft[0],topleft[1]+(rect.height*line_num))
                rect.topleft=topleft
                line_num+=1
                #add to our list the current txt line...
                txt.append((temp_var,rect))
        #return a list of img's to blit and thier rects...
        self.txt_surf_list=txt
        
    def blit(self,screen,rect=None):
        if rect == None:
            rect = self.options.rect
        if rect != self.__old_rect:
            self.options.rect=rect
            self.render()
        for line in self.txt_surf_list:
            screen.blit(line[0],line[1])
        pygame.draw.rect(screen,(255,255,255),self.options.rect,1)
                