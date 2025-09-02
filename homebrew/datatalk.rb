class Datatalk < Formula
  include Language::Python::Virtualenv

  desc "Query CSV and Parquet data with natural language"
  homepage "https://github.com/vtsaplin/datatalk"
  url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
  sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  license "MIT"
  head "https://github.com/vtsaplin/datatalk.git", branch: "main"

  depends_on "python@3.12"

  # Runtime dependencies (auto-generated from uv.lock)
  resource "annotated-types" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "anyio" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "certifi" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "distro" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "duckdb" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "h11" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "httpcore" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "httpx" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "idna" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "jiter" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "markdown-it-py" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "mdurl" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "openai" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "pandas" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "pydantic" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "pydantic-core" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "pygments" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "python-dateutil" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "python-dotenv" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "pytz" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "rich" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "six" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "sniffio" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "tqdm" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "typing-extensions" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "typing-inspection" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  resource "tzdata" do
    url "https://github.com/vtsaplin/datatalk/archive/refs/tags/v0.1.5.tar.gz"
    sha256 "4fa2fe35c9b4d23dcb35bef768d3ca918cd7b2f48a98a9745609429aaf069822"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/datatalk", "--help"
  end
end
