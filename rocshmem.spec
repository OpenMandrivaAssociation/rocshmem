# GPU-side OpenSHMEM. TheRock 10.0.

Name:		rocshmem
Version:	10.0.0
Release:	1
Summary:	OpenSHMEM for HIP/ROCm
License:	MIT
Group:		System/Libraries
URL:		https://github.com/ROCm/rocm-systems
Source0:	%{rocm_systems_source rocshmem}

BuildRequires:	rocm-rpm-macros
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	rocm-cmake
BuildRequires:	hipcc
BuildRequires:	rocm-hip-devel
BuildRequires:	rocm-runtime-devel
BuildRequires:	cmake(amd_smi)
BuildRequires:	cmake(rocprofiler-register)
BuildRequires:	pkgconfig(numa)

ExclusiveArch:	%{x86_64} %{aarch64}

%description
rocSHMEM is a GPU-initiated OpenSHMEM implementation used by some
RCCL GIN paths and multi-GPU research codes.

%package devel
Summary:	Development files for %{name}
Group:		Development/C++
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	rocm-hip-devel

%description devel
Headers and CMake package for rocSHMEM.

%prep
%autosetup -n rocshmem -p1

%build
export CXX=hipcc
export CC=clang
CXXFLAGS=$(printf '%s' "%{optflags}" | sed 's/-mfpmath=sse//g')
export CXXFLAGS
%cmake %{rocm_cmake_fhs} %{rocm_cmake_gpu_targets} \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_CXX_COMPILER=hipcc \
	-DCMAKE_CXX_FLAGS="$CXXFLAGS" \
	-DBUILD_FUNCTIONAL_TESTS=OFF \
	-DBUILD_UNIT_TESTS=OFF \
	-DBUILD_EXAMPLES=OFF \
	-DBUILD_PYTHON_BINDING=OFF \
	-DUSE_EXTERNAL_MPI=OFF \
	-DUSE_IPC=ON \
	-DUSE_RO=OFF \
	-DROCM_PATH=%{_prefix} \
	-DCMAKE_PREFIX_PATH=%{_prefix} \
	-G Ninja
%ninja_build -C build

%install
%ninja_install -C build

%files
%license LICENSE.md
%doc README.md CHANGELOG.md
%{_libdir}/librocshmem.so.*
%{_bindir}/rocshmem_info

%files devel
%{_includedir}/rocshmem/
%{_includedir}/rocshmem.h
%{_libdir}/librocshmem.so
%{_libdir}/cmake/rocshmem/
