from django.core.management.base import BaseCommand
from firebase_admin import firestore
from apps.customauth.models import CustomUser
from apps.customauth.firebase import initialize_firebase


class Command(BaseCommand):
    help = 'Fetch users from Firestore "users" collection and sync to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-type',
            type=str,
            default='creator',
            choices=['creator', 'admin', 'staff'],
            help='Default user type for synced users (default: creator)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )

    def handle(self, *args, **options):
        # Initialize Firebase
        try:
            initialize_firebase()
            self.stdout.write(self.style.SUCCESS('✓ Firebase initialized'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to initialize Firebase: {str(e)}'))
            return

        # Get Firestore client
        try:
            db = firestore.client()
            self.stdout.write(self.style.SUCCESS('✓ Connected to Firestore'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to connect to Firestore: {str(e)}'))
            return

        # Fetch users from Firestore
        try:
            users_ref = db.collection('users')
            firestore_users = users_ref.stream()
            self.stdout.write(self.style.SUCCESS('✓ Fetched users from Firestore'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to fetch users from Firestore: {str(e)}'))
            return

        # Process and sync users
        user_type = options['user_type']
        dry_run = options['dry_run']
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('SYNCING USERS FROM FIRESTORE')
        self.stdout.write('=' * 60 + '\n')

        for user_doc in firestore_users:
            try:
                user_data = user_doc.to_dict()
                user_id = user_doc.id
                # Extract required fields
                email = user_data.get('email', '').strip().lower()
                username = user_data.get('username', user_data.get('slug')).strip().lower()
                first_name = user_data.get('firstName', user_data.get('first_name', '')).strip()
                last_name = user_data.get('lastName', user_data.get('last_name', '')).strip()
                phone_number = user_data.get('phoneNumber', user_data.get('phone_number', '')).strip()

                # Skip if missing email, if username is missing, use email as username
                if not email:
                    self.stdout.write(
                        self.style.WARNING(f'⊘ Skipped user {user_id}: missing email')
                    )
                    skipped_count += 1
                    continue
                          
                # Prepare user data
                user_defaults = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': phone_number,
                    'user_type': user_type,
                }

                if not dry_run:
                    # Create or update user
                    user_obj, created = CustomUser.objects.update_or_create(
                        email=email,
                        defaults={
                            'username': username,
                            **user_defaults
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Created user: {email} ({username})')
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'↻ Updated user: {email} ({username})')
                        )
                else:
                    # Dry run - just show what would be created/updated
                    try:
                        existing_user = CustomUser.objects.get(email=email)
                        updated_count += 1
                        self.stdout.write(
                            f'↻ [DRY RUN] Would update user: {email} ({username})'
                        )
                    except CustomUser.DoesNotExist:
                        created_count += 1
                        self.stdout.write(
                            f'✓ [DRY RUN] Would create user: {email} ({username})'
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing user {user_id}: {str(e)}')
                )
                skipped_count += 1
                continue

        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('SYNC SUMMARY')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✓ Created: {created_count}'))
        self.stdout.write(self.style.WARNING(f'↻ Updated: {updated_count}'))
        self.stdout.write(self.style.ERROR(f'⊘ Skipped: {skipped_count}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN MODE] - No changes were made to the database'))

        self.stdout.write('\n')
