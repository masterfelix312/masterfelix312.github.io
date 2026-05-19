require "minitest/autorun"
require "pathname"
require "yaml"
require "date"

class SiteContentTest < Minitest::Test
  ROOT = Pathname.new(__dir__).join("..").expand_path

  def test_config_has_required_fields
    config = yaml_load((ROOT / "_config.yml").read)

    %w[name description avatar].each do |key|
      assert config[key].to_s.strip != "", "Expected _config.yml to define #{key}"
    end

    avatar = config["avatar"].to_s.strip
    return if avatar.match?(/\Ahttps?:\/\//)

    avatar_path = ROOT / avatar.sub(%r{\A\./}, "").sub(%r{\A/}, "")
    assert avatar_path.exist?, "Expected avatar file to exist at #{avatar_path}"
  end

  def test_layouts_reference_existing_includes
    includes_dir = ROOT / "_includes"
    layout_files.each do |layout_path|
      extract_includes(layout_path.read).each do |include_name|
        include_path = includes_dir / include_name
        assert include_path.exist?, "Missing include #{include_name} referenced by #{layout_path}"
      end
    end
  end

  def test_root_pages_have_valid_front_matter
    root_page_files.each do |page_path|
      front_matter = read_front_matter(page_path)
      next if front_matter.empty?
      assert front_matter["layout"].to_s.strip != "", "Missing layout in #{page_path}"
      assert layout_exists?(front_matter["layout"]), "Unknown layout #{front_matter['layout']} in #{page_path}"

      next if page_path.basename.to_s == "index.html"

      assert front_matter["title"].to_s.strip != "", "Missing title in #{page_path}"
    end
  end

  def test_posts_have_required_front_matter
    post_files.each do |post_path|
      front_matter = read_front_matter(post_path)
      assert front_matter["layout"].to_s.strip != "", "Missing layout in #{post_path}"
      assert front_matter["title"].to_s.strip != "", "Missing title in #{post_path}"
      assert layout_exists?(front_matter["layout"]), "Unknown layout #{front_matter['layout']} in #{post_path}"
    end
  end

  def test_layouts_have_valid_parent_layouts
    layout_names = layout_files.map { |path| path.basename(".html").to_s }
    layout_files.each do |layout_path|
      front_matter = read_front_matter(layout_path)
      parent_layout = front_matter["layout"]
      next if parent_layout.to_s.strip == ""

      assert layout_names.include?(parent_layout), "Unknown parent layout #{parent_layout} in #{layout_path}"
    end
  end

  def test_local_images_exist
    image_paths = content_files.flat_map { |path| extract_image_paths(path.read) }
    normalized = image_paths.map { |path| normalize_image_path(path) }.compact.uniq

    normalized.each do |image_path|
      assert (ROOT / image_path).exist?, "Missing image file #{image_path}"
    end
  end

  private

  def layout_files
    Dir.glob(ROOT.join("_layouts", "*.html")).map { |path| Pathname.new(path) }
  end

  def root_page_files
    Dir.glob(ROOT.join("*.{md,html}")).map { |path| Pathname.new(path) }
  end

  def post_files
    Dir.glob(ROOT.join("_posts", "*.{md,markdown}")).map { |path| Pathname.new(path) }
  end

  def content_files
    patterns = [
      ROOT.join("*.{md,html}"),
      ROOT.join("_posts", "*.{md,markdown}"),
      ROOT.join("_layouts", "*.html"),
      ROOT.join("_includes", "*.html")
    ]
    patterns.flat_map { |pattern| Dir.glob(pattern) }.map { |path| Pathname.new(path) }
  end

  def read_front_matter(path)
    content = path.read
    match = content.match(/\A---\s*\n(.*?)\n---\s*(\n|$)/m)
    return {} unless match

    yaml_load(match[1])
  end

  def extract_includes(content)
    content.scan(/\{%\s*include\s+([^\s%]+)\s*%\}/).flatten
  end

  def extract_image_paths(content)
    paths = []
    content.scan(/!\[[^\]]*\]\(([^)]+)\)/) { |match| paths << match.first }
    content.scan(/<img[^>]+src=["']([^"']+)["']/i) { |match| paths << match.first }
    paths
  end

  def normalize_image_path(path)
    return nil if path.nil? || path.strip == ""
    return nil if path.match?(/\Ahttps?:\/\//)

    normalized = path.gsub(/\{\{\s*site\.baseurl\s*\}\}/, "").strip
    normalized = normalized.split(/\s+/).first.to_s
    normalized = normalized.sub(/\A\.\//, "").sub(/\A\//, "")
    return nil unless normalized.start_with?("images/")

    normalized
  end

  def layout_exists?(layout_name)
    return false if layout_name.to_s.strip == ""

    (ROOT / "_layouts" / "#{layout_name}.html").exist?
  end

  def yaml_load(content)
    YAML.safe_load(content, permitted_classes: [Date, Symbol], aliases: true) || {}
  end
end
