# Testing Comment Removal Feature

## Step 0: Install Dependencies (if needed)

If you encounter a `ModuleNotFoundError: No module named 'decouple'`, install the required package:

```bash
pip3 install python-decouple
```

Or if you're using a virtual environment:
```bash
pip install python-decouple
```

## Step 1: Apply Database Migrations

First, you need to apply the migration to create the Comment table in your database:

```bash
python3 manage.py migrate
```

## Step 2: Create/Verify Admin Account

If you don't have an admin account yet, create one:

```bash
python3 manage.py createsuperuser
```

Follow the prompts to create a username, email, and password.

If you already have an admin account but forgot the password:
```bash
python3 manage.py changepassword <username>
```

## Step 3: Start the Development Server

```bash
python3 manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## Step 4: Test the Comment System

### 4a. Create Test Comments

1. Navigate to `http://127.0.0.1:8000/news/`
2. Click on any news article to view its detail page
3. If you're not logged in, create a regular user account or log in
4. Scroll down to the comments section
5. Post a few test comments (you can post inappropriate content for testing purposes)

### 4b. Test Admin Comment Removal

1. Log out of your regular user account
2. Navigate to `http://127.0.0.1:8000/admin/`
3. Log in with your admin credentials
4. In the admin panel, you should see a "Comments" section under "News"
5. Click on "Comments"
6. You'll see a list of all comments with:
   - Content preview (first 50 characters)
   - Author
   - Article
   - Created date
7. Test the features:
   - **Search**: Use the search box to find comments by content, author, or article title
   - **Filter**: Use the filters on the right to filter by date or article
   - **Delete single comment**: Click on a comment, then click "Delete" button
   - **Bulk delete**: Select multiple comments using checkboxes, choose "Delete selected comments" from the action dropdown, and click "Go"

## Step 5: Verify Comments Are Removed

1. After deleting comments from the admin panel
2. Navigate back to the news article page
3. Verify that the deleted comments no longer appear

## Quick Test Checklist

- [ ] Migration applied successfully
- [ ] Admin account exists and can log in
- [ ] Can create comments on news articles
- [ ] Comments appear on the news detail page
- [ ] Can access admin panel at `/admin/`
- [ ] Can see Comments section in admin
- [ ] Can search for comments
- [ ] Can filter comments
- [ ] Can delete individual comments
- [ ] Can bulk delete multiple comments
- [ ] Deleted comments no longer appear on the article page

## Troubleshooting

If you encounter issues:

1. **Migration errors**: Make sure you're in the project directory and have activated your virtual environment
2. **Admin not showing Comments**: Check that the migration was applied: `python3 manage.py showmigrations news`
3. **Can't log in to admin**: Verify your user has `is_staff` and `is_superuser` set to True
4. **Comments not showing**: Check that you're viewing an article that has comments, and that the view is loading comments correctly

