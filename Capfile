load 'deploy' if respond_to?(:namespace)
# =============================================================================
# REQUIRED VARIABLES
# =============================================================================
set :scm, :git
set :application, "fumblerooski"
set :repository, "dwillis@github.com:/dwillis/fumblerooski/tree/master"

# =============================================================================
# ROLES
# =============================================================================
role :app, "dwillis.webfactional.com"
role :web, "dwillis.webfactional.com"
role :db,  "dwillis.webfactional.com", :primary => true

# =============================================================================
# OPTIONAL VARIABLES
# =============================================================================
set :keep_releases, 3
set :deploy_to, "/home/dwillis/webapps/django/fumblerooski"
set :user, "dwillis"
set :use_sudo, false
set :group_writable, true

# =============================================================================
# TASKS
# =============================================================================
namespace :deploy do
  after 'deploy:restart', 'deploy:cleanup'
  after 'deploy:symlink', 'deploy:files'  

  before 'deploy', 'web:disable'
  after 'deploy', 'web:enable'
  
  desc "Install settings and media files"
  task :files, :roles => :app, :except => { :no_release => true } do
    run "ln -nfs #{shared_path}/system/settings.py #{release_path}/settings.py"
    run "ln -nfs #{shared_path}/media/ #{release_path}/media"
    run "ln -nfs #{shared_path}/cache/ #{release_path}/cache"
  end
  
  desc "Restarts your application"
  task :restart, :roles => :app, :except => { :no_release => true } do
    sudo "/etc/init.d/apache2 reload"
  end
  
  desc "Start the application servers"
  task :start, :roles => :app do
    sudo "/etc/init.d/apache2 start"
  end
  
  desc "[internal] Touches up the released code"
  task :finalize_update, :except => { :no_release => true } do
    run "chmod -R g+w #{latest_release}" if fetch(:group_writable, true)
  end
  
  desc "Deploys and starts a `cold' application"
  task :cold do
    update
    start
  end
  
  desc "Prepares one or more servers for deployment"
  task :setup, :except => { :no_release => true } do
    dirs = [deploy_to, releases_path, shared_path]
    dirs += %w(system media cache).map { |d| File.join(shared_path, d) }
    run "umask 02 && mkdir -p #{dirs.join(' ')}"
  end
end

namespace :web do
  # Theses tasks requires an RewriteRule in your Apache configuration
  desc "Present a maintenance page to visitors"
  task :disable, :roles => :web, :except => { :no_release => true } do
    require 'erb'
    on_rollback {
      run "rm #{shared_path}/media/maintenance.html"
    }

    reason = ENV['REASON']
    deadline = ENV['UNTIL']

    template = File.read(File.join(File.dirname(__FILE__), "templates", "maintenance.rhtml"))
    result = ERB.new(template).result(binding)

    put result, "#{shared_path}/media/maintenance.html", :mode => 0644
  end
  
  desc "Makes the application web-accessible again"
  task :enable, :roles => :web, :except => { :no_release => true } do
    run "rm #{shared_path}/media/maintenance.html"
  end
end
