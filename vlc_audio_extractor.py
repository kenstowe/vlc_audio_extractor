import os
import subprocess
import wx


class Arrow(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs, size=(110, 20))

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.SetBackgroundColour('white')

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        pen = wx.Pen(wx.Colour(232, 94, 0), width=3, style=wx.PENSTYLE_SOLID)
        dc.SetPen(pen)
        dc.DrawLine(0, 10, 70, 10)
        dc.DrawLine(70, 10, 60, 5)
        dc.DrawLine(70, 10, 60, 15)


class MainWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.files = ''
        self.working_dir = ''
        self.output_dir = ''
        self.file_name = ''

        self.init_ui()
        self.Centre()
        self.Show(True)

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(0, 0)
        self.SetBackgroundColour('white')

        # Stage one, select files
        files_text = wx.StaticText(panel, label="Select file(s)")
        sizer.Add(files_text, pos=(2, 4), flag=wx.ALL, border=5)

        self.files_ctrl = wx.TextCtrl(panel)
        sizer.Add(self.files_ctrl, pos=(3, 1), span=(1, 5), flag=wx.EXPAND | wx.ALL, border=5)

        files_button = wx.Button(panel, label="Browse", size=(80, 23))
        sizer.Add(files_button, pos=(3, 6), flag=wx.ALIGN_CENTRE)
        files_button.Bind(wx.EVT_BUTTON, self.get_files)

        arrow1 = Arrow(self, wx.ID_ANY)
        sizer.Add(arrow1, pos=(3, 7), flag=wx.LEFT | wx.ALIGN_CENTRE, border=30)

        # Stage two, select output dir
        output_text = wx.StaticText(panel, label="Select output folder")
        sizer.Add(output_text, pos=(2, 9), flag=wx.ALL, border=5)

        self.dir_ctrl = wx.DirPickerCtrl(panel, message="Select output folder")
        sizer.Add(self.dir_ctrl, pos=(3, 8), span=(1, 5), flag=wx.EXPAND | wx.ALL, border=5)
        self.dir_ctrl.Bind(wx.EVT_DIRPICKER_CHANGED, self.set_dir)

        arrow2 = Arrow(self, wx.ID_ANY)
        sizer.Add(arrow2, pos=(3, 14), flag=wx.LEFT | wx.ALIGN_CENTRE, border=15)

        # Stage three, Set output name
        name_text = wx.StaticText(panel, label="Set output name")
        sizer.Add(name_text, pos=(2, 17), flag=wx.ALL, border=5)

        self.name_ctrl = wx.TextCtrl(panel)
        sizer.Add(self.name_ctrl, pos=(3, 15), span=(1, 6), flag=wx.EXPAND | wx.ALL, border=5)
        self.name_ctrl.Bind(wx.EVT_TEXT, self.set_name)

        arrow3 = Arrow(self, wx.ID_ANY)
        sizer.Add(arrow3, pos=(3, 22), flag=wx.LEFT | wx.ALIGN_CENTRE, border=15)

        # Stage four, start
        start_button = wx.Button(panel, label="Start", size=(90, 28))
        sizer.Add(start_button, pos=(3, 23))
        start_button.Bind(wx.EVT_BUTTON, self.start_transcode)

        panel.SetSizerAndFit(sizer)

    def on_open(self):
        with wx.FileDialog(self, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            filenames = fileDialog.GetFilenames()
            directory = fileDialog.GetDirectory()

        return filenames, directory

    def get_files(self, event):
        files_string = ''
        i = 0

        # get files and working dir
        files_list, files_dir = self.on_open()
        while i < len(files_list):
            files_string = f'{files_string} \"{files_list[i]}\"'
            i += 1

        self.working_dir = files_dir
        self.files = files_string
        self.files_ctrl.SetValue(self.files)

        # set auto fill output dir
        self.dir_ctrl.SetPath(files_dir)
        self.output_dir = files_dir

        # set auto fill name
        if len(files_list) == 1:
            self.name_ctrl.SetValue(os.path.splitext(files_list[0])[0])
        else:
            self.name_ctrl.SetValue(os.path.basename(files_dir))

    def set_dir(self, event):
        self.output_dir = event.GetPath()

    def set_name(self, event):
        self.file_name = event.GetString()

    def start_transcode(self, event):
        destination = f"\"\'{self.output_dir}\\{self.file_name}.mp3\'\""
        # Triple quotes are required. outer is for python, middle is for windows command line, inner is for VLC

        command = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
        options = fr'--no-sout-video --sout-audio --sout-keep --sout=#gather:transcode{{acodec=mp3,ab=128,channels=2,\
                    samplerate=44100}}:standard{{access=file,mux=dummy,dst={destination}}}'

        if self.files and self.working_dir and self.output_dir and self.file_name:
            command_options = f'{command} {self.files} {options}'

            print('Final Command:')
            print(command_options)

            subprocess.run(command_options, cwd=self.working_dir)


def main():
    app = wx.App(False)
    frame = MainWindow(None, title='VLC Audio Extractor', size=(1200, 200))
    app.MainLoop()


if __name__ == "__main__":
    main()


# TODO: Find out if VLC can run as background task with status shown in wxpython window

# TODO: Add in support for choosing 1 or multiple directories for source
