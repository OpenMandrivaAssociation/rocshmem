# GPU-side OpenSHMEM. TheRock 10.1.

Name:		rocshmem
Version:	10.1.0
Release:	1
Summary:	OpenSHMEM for HIP/ROCm
License:	MIT
Group:		System/Libraries
URL:		https://github.com/ROCm/rocm-systems
Source0:	https://github.com/ROCm/rocm-systems/releases/download/therock-10.1/rocshmem.tar.gz#/rocshmem-%{version}.tar.gz
# hsakmt's imported interface passes bare -ldrm. clang-linker-wrapper
# treats that as a device bitcode library.
Patch0:		0001-hsakmt-host-link.patch
# No NUMAConfig.cmake in the distro. Bake libnuma instead of find_dependency(NUMA).
Patch1:		0002-bake-libnuma-into-cmake.patch

BuildRequires:	rocm-rpm-macros
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	rocm-cmake
BuildRequires:	hipcc
BuildRequires:	rocm-hip-devel
BuildRequires:	cmake(AMDDeviceLibs)
BuildRequires:	rocm-runtime-devel
BuildRequires:	cmake(rocm-core)
BuildRequires:	cmake(amd_smi)
BuildRequires:	cmake(rocprofiler-register)
BuildRequires:	cmake(hsakmt)
BuildRequires:	pkgconfig(numa)
# libdrm.so (the -devel symlink) has to be present for the host link.
BuildRequires:	pkgconfig(libdrm)
BuildRequires:	clang-tools
BuildRequires:	clang >= %{rocm_llvm_maj_ver}

%description
rocSHMEM is a GPU-initiated OpenSHMEM implementation used by some
RCCL GIN paths and multi-GPU research codes.

%package devel
Summary:	Development files for %{name}
Group:		Development/C++
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	rocm-hip-devel
# The exported cmake target points at libnuma.so and numa.h.
Requires:	pkgconfig(numa)

%description devel
Headers and CMake package for rocSHMEM.

%prep
%autosetup -n rocshmem -p1

%build
export CXX=hipcc
export CC=clang
export HIP_CLANG_PATH=%{_bindir}
CXXFLAGS=$(printf '%s' "%{optflags}" | sed 's/-mfpmath=sse//g')
export CXXFLAGS
# rocshmem_info is a host program, but hip::device still hip-links it.
# lld --gc-sections (LTO) then drops __start/__stop_llvm_offload_entries.
LDFLAGS="${LDFLAGS} -Wl,-z,nostart-stop-gc"
export LDFLAGS
# gin_anvil_sdma_factory.cpp is always compiled; anvil.cpp is not unless USE_SDMA is on.
%cmake %{rocm_cmake_fhs} %{rocm_cmake_gpu_targets} \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_CXX_COMPILER=hipcc \
	-DCMAKE_HIP_COMPILER=clang++ \
	-DCMAKE_HIP_FLAGS="--rocm-path=%{_prefix} --rocm-device-lib-path=%{_libdir}/amdgcn/bitcode" \
	-DCMAKE_HIP_ARCHITECTURES="%{rocm_gpu_targets}" \
	-DCMAKE_CXX_FLAGS="$CXXFLAGS" \
	-DBUILD_FUNCTIONAL_TESTS=OFF \
	-DBUILD_UNIT_TESTS=OFF \
	-DBUILD_EXAMPLES=OFF \
	-DBUILD_PYTHON_BINDING=OFF \
	-DUSE_EXTERNAL_MPI=OFF \
	-DUSE_IPC=ON \
	-DUSE_RO=OFF \
	-DUSE_SDMA=ON \
	-DEXPLICIT_ROCM_VERSION=%{version} \
	-DROCM_PATH=%{_prefix} \
	-DCMAKE_PREFIX_PATH=%{_prefix} \
	-G Ninja
%ninja_build

%install
%ninja_install -C build
# %license owns LICENSE.md. The cmake install also copies it under doc.
rm -f %{buildroot}%{_docdir}/rocshmem/LICENSE.md
rmdir %{buildroot}%{_docdir}/rocshmem 2>/dev/null || true

%files
%license LICENSE.md
%doc README.md CHANGELOG.md
# Upstream sets no SOVERSION. The library file is librocshmem.so itself.
%{_libdir}/librocshmem.so
%{_bindir}/rocshmem_info

%files devel
%{_includedir}/rocshmem/
%{_includedir}/gin_anvil/
%{_libdir}/cmake/rocshmem/
