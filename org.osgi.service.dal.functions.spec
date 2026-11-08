Name:		org.osgi.service.dal.functions
Version:	1.0.1
Release:	1
Summary:	OSGi Device Abstraction Layer functions
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.dal.functions/%{version}/org.osgi.service.dal.functions-%{version}-sources.jar
Source1:	https://raw.githubusercontent.com/osgi/osgi/r8-cmpn-final/LICENSE#/org.osgi.service.dal.functions-%{version}-LICENSE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildRequires:	mvn(org.osgi:org.osgi.service.dal)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi Device Abstraction Layer functions 1.0. Controls, sensors, and their
data types. They extend Function and FunctionData from the packaged Device
Abstraction Layer 1.0.2. Upstream asked for 1.0.1. The versioning
annotation is provided from osgi.annotation 8.1.0. Upstream asked for
8.0.1. This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

root = Path("src/main/java/org/osgi/service/dal/functions")
names = sorted(path.name for path in root.glob("*.java"))
expect = [
    "Alarm.java",
    "BooleanControl.java",
    "BooleanSensor.java",
    "Keypad.java",
    "Meter.java",
    "MultiLevelControl.java",
    "MultiLevelSensor.java",
    "Types.java",
    "WakeUp.java",
    "package-info.java",
]
if names != expect:
    raise SystemExit("java files " + " ".join(names))
data = sorted(path.name for path in (root / "data").glob("*.java"))
expect_data = [
    "AlarmData.java",
    "BooleanData.java",
    "Comparator.java",
    "KeypadData.java",
    "LevelData.java",
    "package-info.java",
]
if data != expect_data:
    raise SystemExit("data java files " + " ".join(data))
for path in (root / "package-info.java", root / "data" / "package-info.java"):
    if '@Version("1.0.1")' not in path.read_text(encoding="utf-8"):
        raise SystemExit("package-info version changed " + str(path))
if list(Path(".").rglob("packageinfo")):
    raise SystemExit("unexpected packageinfo")
if "Apache License" not in Path("LICENSE").read_text(encoding="utf-8"):
    raise SystemExit("LICENSE is not the Apache license")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.dal.functions</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:org.osgi.service.dal.functions</name>
  <description>OSGi Device Abstraction Layer functions.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.service.dal</artifactId>
      <version>1.0.2</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.service.dal.functions</artifactId>",
    "<artifactId>org.osgi.service.dal</artifactId>",
    "<version>1.0.2</version>",
    "<artifactId>osgi.annotation</artifactId>",
    "<version>8.1.0</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "</project.build.sourceEncoding>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "felix", "maven-bundle-plugin", "<version>8.0.1</version>", "org.osgi.util.function", "projectbuild.sourceEncoding"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
# The package version is 1.0.1. The DAL dependency must not stay at 1.0.1.
if pom.count("<version>1.0.1</version>") != 1:
    raise SystemExit("unexpected 1.0.1 version count")
PY

%build -a
java --module-path target/org.osgi.service.dal.functions-%{version}.jar --describe-module org.osgi.service.dal.functions > module-describe.txt
grep -q '^org.osgi.service.dal.functions' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.service.dal.functions-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    names = set(zf.namelist())
required = {
    "org/osgi/service/dal/functions/package-info.class",
    "org/osgi/service/dal/functions/Alarm.class",
    "org/osgi/service/dal/functions/BooleanControl.class",
    "org/osgi/service/dal/functions/BooleanSensor.class",
    "org/osgi/service/dal/functions/Keypad.class",
    "org/osgi/service/dal/functions/Meter.class",
    "org/osgi/service/dal/functions/MultiLevelControl.class",
    "org/osgi/service/dal/functions/MultiLevelSensor.class",
    "org/osgi/service/dal/functions/Types.class",
    "org/osgi/service/dal/functions/WakeUp.class",
    "org/osgi/service/dal/functions/data/package-info.class",
    "org/osgi/service/dal/functions/data/AlarmData.class",
    "org/osgi/service/dal/functions/data/BooleanData.class",
    "org/osgi/service/dal/functions/data/Comparator.class",
    "org/osgi/service/dal/functions/data/KeypadData.class",
    "org/osgi/service/dal/functions/data/LevelData.class",
}
missing = sorted(required - names)
if missing:
    raise SystemExit("missing " + " ".join(missing))
if any(name.endswith("packageinfo") for name in names):
    raise SystemExit("unexpected packageinfo")
PY

%files -f .mfiles
%doc LICENSE
