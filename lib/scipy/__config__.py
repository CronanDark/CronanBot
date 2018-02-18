# This file is generated by D:\Build\scipy\scipy-0.19.x-git\setup.py
# It contains system_info results at the time of building this package.
__all__ = ["get_info","show"]

blas_mkl_info={'libraries': ['mkl_lapack95_lp64', 'mkl_blas95_lp64', 'mkl_rt'], 'include_dirs': ['C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl', 'C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl\\include', 'C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl\\lib', 'C:/Program Files (x86)/IntelSWTools/compilers_and_libraries_2017/windows/mkl/include'], 'define_macros': [('SCIPY_MKL_H', None), ('HAVE_CBLAS', None)], 'library_dirs': ['C:/Program Files (x86)/IntelSWTools/compilers_and_libraries_2017/windows/mkl/lib/intel64_win']}
lapack_opt_info={'libraries': ['mkl_lapack95_lp64', 'mkl_blas95_lp64', 'mkl_rt'], 'include_dirs': ['C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl', 'C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl\\include', 'C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl\\lib', 'C:/Program Files (x86)/IntelSWTools/compilers_and_libraries_2017/windows/mkl/include'], 'define_macros': [('SCIPY_MKL_H', None), ('HAVE_CBLAS', None)], 'library_dirs': ['C:/Program Files (x86)/IntelSWTools/compilers_and_libraries_2017/windows/mkl/lib/intel64_win']}
openblas_lapack_info={}
lapack_mkl_info={'libraries': ['mkl_lapack95_lp64', 'mkl_blas95_lp64', 'mkl_rt'], 'include_dirs': ['C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl', 'C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl\\include', 'C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl\\lib', 'C:/Program Files (x86)/IntelSWTools/compilers_and_libraries_2017/windows/mkl/include'], 'define_macros': [('SCIPY_MKL_H', None), ('HAVE_CBLAS', None)], 'library_dirs': ['C:/Program Files (x86)/IntelSWTools/compilers_and_libraries_2017/windows/mkl/lib/intel64_win']}
blas_opt_info={'libraries': ['mkl_lapack95_lp64', 'mkl_blas95_lp64', 'mkl_rt'], 'include_dirs': ['C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl', 'C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl\\include', 'C:\\Program Files (x86)\\IntelSWTools\\compilers_and_libraries_2017\\windows\\mkl\\lib', 'C:/Program Files (x86)/IntelSWTools/compilers_and_libraries_2017/windows/mkl/include'], 'define_macros': [('SCIPY_MKL_H', None), ('HAVE_CBLAS', None)], 'library_dirs': ['C:/Program Files (x86)/IntelSWTools/compilers_and_libraries_2017/windows/mkl/lib/intel64_win']}

def get_info(name):
    g = globals()
    return g.get(name, g.get(name + "_info", {}))

def show():
    for name,info_dict in globals().items():
        if name[0] == "_" or type(info_dict) is not type({}): continue
        print(name + ":")
        if not info_dict:
            print("  NOT AVAILABLE")
        for k,v in info_dict.items():
            v = str(v)
            if k == "sources" and len(v) > 200:
                v = v[:60] + " ...\n... " + v[-60:]
            print("    %s = %s" % (k,v))
    