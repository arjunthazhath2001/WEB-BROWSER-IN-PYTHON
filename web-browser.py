import socket
import ssl
import tkinter

class URL:
    def __init__(self,url):
        self.scheme, url= url.split("://",1)
        assert self.scheme in ["http","https"]
        
        if(self.scheme=="http"):
            self.port=80
        elif self.scheme=="https":
            self.port=443
        
        if "/" not in url:
            url= url+"/"
        self.host,url= url.split("/",1)
        self.path= "/"+url
        
        if ":" in self.host:
            self.host, port= self.host.split(":",1) 
            self.port= int(port)

    def request(self):
        s= socket.socket(
            family= socket.AF_INET,
            type= socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        
        s.connect((self.host,self.port))
        if self.scheme=="https":
            ctx= ssl.create_default_context()
            s= ctx.wrap_socket(s, server_hostname=self.host)
        
        request= "GET {} HTTP/1.0\r\n".format(self.path)
        request+= "Host: {}\r\n".format(self.host)
        request+= "\r\n"
        s.send(request.encode("utf-8"))
        
        response= s.makefile("r", encoding="utf-8", newline="\r\n")
        
        statusline= response.readline()
        version,status,explanation= statusline.split(" ",2)
        
        response_headers={}
        while True:
            line= response.readline()
            if line == "\r\n" : break
            header,value= line.split(":",1)
            response_headers[header.casefold()]= value.strip()
        
        
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content= response.read()
        s.close()
        return content
    
    
def lex(body):
    text=""
    in_tag= False
    for c in body:
        if c=="<":
            in_tag=True
        elif c==">":
            in_tag=False
        elif not in_tag:
            text +=c
    return text            


HSTEP, VSTEP= 13,18

def layout(text):
    
    display_list=[]
    cursor_x, cursor_y= HSTEP, VSTEP
    
    for c in text:
        if c=="\n":
            cursor_y += VSTEP*1.5
            cursor_x= HSTEP        
        else:
            display_list.append((cursor_x,cursor_y,c))
            cursor_x += HSTEP
            if cursor_x>= WIDTH-HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
    return display_list



SCROLL_STEP=100
WIDTH, HEIGHT= 800,600

class Browser:
    def __init__(self):
        self.window= tkinter.Tk()
        self.canvas= tkinter.Canvas(self.window,width=WIDTH,height=HEIGHT)
        self.canvas.pack()
        self.scroll=0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Button-4>", self.scrollup)
        self.window.bind("<MouseWheel>", self.on_mousewheel)
        self.window.bind("<Button-5>", self.scrolldown)
    
    
    def on_mousewheel(self,e):
        delta= -1 * (e.delta//120)
        self.scroll= max(0, self.scroll+ delta* SCROLL_STEP)
        self.draw() 
      

    def scrollup(self,e):
        self.scroll = max(0, self.scroll-SCROLL_STEP)
        self.draw()
        
    def scrolldown(self,e):
        self.scroll += SCROLL_STEP
        self.draw()
    
    def draw(self):
        self.canvas.delete("all")
        for x,y,c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            
            self.canvas.create_text(x,y-self.scroll,text=c)
            
    def load(self,url):
        body= url.request()
        text=lex(body)
        self.display_list= layout(text)
        self.draw()
        
            
    
if __name__=="__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()