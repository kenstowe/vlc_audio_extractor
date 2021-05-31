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

        arrow1 = Arrow(self, wx.ID_ANY)
        sizer.Add(arrow1, pos=(3, 7), flag=wx.LEFT | wx.ALIGN_CENTRE, border=30)

        # Stage two, select output dir
        output_text = wx.StaticText(panel, label="Select output folder")
        sizer.Add(output_text, pos=(2, 9), flag=wx.ALL, border=5)

        self.dir_ctrl = wx.DirPickerCtrl(panel, message="Select output folder")
        sizer.Add(self.dir_ctrl, pos=(3, 8), span=(1, 5), flag=wx.EXPAND | wx.ALL, border=5)

        arrow2 = Arrow(self, wx.ID_ANY)
        sizer.Add(arrow2, pos=(3, 14), flag=wx.LEFT | wx.ALIGN_CENTRE, border=15)

        # Stage three, Set output name
        name_text = wx.StaticText(panel, label="Set output name")
        sizer.Add(name_text, pos=(2, 17), flag=wx.ALL, border=5)

        self.name_ctrl = wx.TextCtrl(panel)
        sizer.Add(self.name_ctrl, pos=(3, 15), span=(1, 6), flag=wx.EXPAND | wx.ALL, border=5)

        arrow3 = Arrow(self, wx.ID_ANY)
        sizer.Add(arrow3, pos=(3, 22), flag=wx.LEFT | wx.ALIGN_CENTRE, border=15)

        # Stage four, start
        start_button = wx.Button(panel, label="Start", size=(90, 28))
        sizer.Add(start_button, pos=(3, 23))

        files_button.Bind(wx.EVT_BUTTON, self.get_files)
        self.dir_ctrl.Bind(wx.EVT_DIRPICKER_CHANGED, self.set_dir)
        self.name_ctrl.Bind(wx.EVT_TEXT, self.set_name)
        start_button.Bind(wx.EVT_BUTTON, self.start_transcode)

        panel.SetSizerAndFit(sizer)

        self.Centre()

        self.vlc_path = self.find_vlc()

    def ask_user_for_vlc(self, vlc_loc_file):
        yes_no = wx.MessageDialog(None, 'VLC not found.\n\nWould you like to select the file location?',
                                  'VLC Audio Extractor', wx.YES_NO | wx.ICON_ERROR | wx.STAY_ON_TOP)

        answer = yes_no.ShowModal()

        if answer == wx.ID_YES:
            with wx.FileDialog(self, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return  # the user changed their mind

                vlc_loc = fileDialog.GetPath()

                with open(vlc_loc_file, 'w') as f:
                    f.write(str(vlc_loc))

            return vlc_loc
        else:
            self.Close()

        yes_no.Destroy()

    def find_vlc(self):
        pf_dir = os.environ["ProgramFiles"]  # The Program File directory (64bit)
        pf86_dir = os.environ["ProgramFiles(x86)"]  # The Program File directory (32bit)
        vlc_root = r'\VideoLAN\VLC\vlc.exe'
        vlc_loc_file = r'vlc_location.txt'

        if os.path.exists(f'{pf_dir}{vlc_root}'):
            return f'{pf_dir}{vlc_root}'
        elif os.path.exists(f'{pf86_dir}{vlc_root}'):
            return f'{pf86_dir}{vlc_root}'
        elif os.path.exists(vlc_loc_file):
            with open(vlc_loc_file, 'r') as f:
                vlc_loc = f.readline().encode('unicode-escape').decode()

                if os.path.exists(vlc_loc):
                    return vlc_loc
                else:
                    return self.ask_user_for_vlc(vlc_loc_file)
        else:
            return self.ask_user_for_vlc(vlc_loc_file)

    def on_open(self):
        with wx.FileDialog(self, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            filenames = fileDialog.GetFilenames()
            directory = fileDialog.GetDirectory()
            paths = fileDialog.GetPaths()

        return filenames, directory, paths

    def get_files(self, event):
        # get files and paths
        selected_files = self.on_open()
        if not selected_files:
            return

        files_list, files_dir, files_path = selected_files

        files_string = '; '.join(file for file in files_list)

        file_paths_string = ' '.join(['"{}"'.format(path) for path in files_path])

        self.files = file_paths_string
        self.files_ctrl.SetValue(files_string)

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

    def start_transcode(self, _):
        destination = f"\"\'{self.output_dir}\\{self.file_name}.mp3\'\""
        # Triple quotes are required. outer is for python, middle is for windows command line, inner is for VLC

        command = fr'{self.vlc_path} --qt-start-minimized'    # flags to start VLC in tray/minimised

        options = f'--no-sout-video --sout-audio --sout-keep --sout=#gather:transcode{{acodec=mp3,ab=128,channels=2,' \
                  f'samplerate=44100}}:standard{{access=file,mux=dummy,dst={destination}}} vlc://quit'

        if self.files and self.output_dir and self.file_name:
            command_options = f'{command} {self.files} {options}'

            print('Final Command:')
            print(command_options)

            subprocess.Popen(command_options)


def main():
    app = wx.App(False)
    frame = MainWindow(None, title='VLC Audio Extraction', size=(1200, 200))
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()


# TODO: Find out if VLC can run as background task with status shown in wxpython window

# TODO: Add in support for choosing 1 or multiple directories for source

# TODO: Add drag and drop support for file select
