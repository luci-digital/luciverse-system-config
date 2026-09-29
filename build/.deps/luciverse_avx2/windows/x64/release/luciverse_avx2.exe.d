{
    files = {
        [[build\.objs\luciverse_avx2\windows\x64\release\src\c\compute_avx2.c.obj]],
        [[build\.objs\luciverse_avx2\windows\x64\release\src\c\dispatch.c.obj]],
        [[build\.objs\luciverse_avx2\windows\x64\release\src\c\main.c.obj]]
    },
    values = {
        [[C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64\link.exe]],
        {
            "-nologo",
            "-dynamicbase",
            "-nxcompat",
            "-machine:x64",
            "/opt:ref",
            "/opt:icf"
        }
    }
}