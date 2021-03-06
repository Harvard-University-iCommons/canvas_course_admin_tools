from unittest import TestCase

from django.test import RequestFactory
from django_auth_lti import const
from mock import patch, ANY, DEFAULT, Mock, MagicMock

from manage_sections.views import section_class_list


@patch.multiple('manage_sections.views.canvas_api_helper_enrollments', get_enrollments=DEFAULT)
@patch.multiple('manage_sections.views.canvas_api_helper_sections', get_section=DEFAULT)
@patch.multiple(
    'manage_sections.views',
    render=DEFAULT,
    SDK_CONTEXT=DEFAULT,
    is_editable_section=DEFAULT,
)
class SectionClassListViewTest(TestCase):
    longMessage = True

    def setUp(self):
        self.canvas_course_id = 1234
        self.section_id = 5678
        self.sis_section_id = 8989
        self.resource_link_id = '1a3b4c5dsdfsdf345345'
        self.request = RequestFactory().get('/fake-path')
        self.request.user = Mock(name='user_mock')
        self.request.user.is_authenticated.return_value = True
        self.request.LTI = {
            'custom_canvas_course_id': self.canvas_course_id,
            'roles': [const.INSTRUCTOR],
            'resource_link_id': self.resource_link_id
        }

    @patch('manage_sections.views.unique_enrollments_not_in_section_filter')
    def test_enrollment_filter_called(self, mock_filter, SDK_CONTEXT, render, get_section, is_editable_section, get_enrollments):
        """
        Test that view function makes a call to unique_enrollments filter with expected args
        """
        section_class_list(self.request, self.section_id)
        mock_filter.assert_called_with(self.section_id, [])

    @patch('manage_sections.views.unique_enrollments_not_in_section_filter')
    def test_view_rendered_on_success(self, mock_filter, SDK_CONTEXT, render, get_section, is_editable_section, get_enrollments):
        """
        Test that view renders expected template on success
        """
        section_class_list(self.request, self.section_id)
        render.assert_called_with(self.request, 'manage_sections/_section_classlist.html', ANY)

    @patch('manage_sections.views._add_badge_label_name_to_enrollments')
    def test_enrollments_sorted_on_success(self, mock_filter, SDK_CONTEXT, render, get_section, is_editable_section, get_enrollments):
        """
        Test that enrollments list is sorted before being passed to render
        """
        enrollments_list_mock = MagicMock(name='enrollments', spec=list)
        mock_filter.return_value = enrollments_list_mock
        section_class_list(self.request, self.section_id)
        # sorting uses a lambda function as key, so just check that it was called
        enrollments_list_mock.sort.assert_called_once_with(key=ANY)

    @patch('manage_sections.views._add_badge_label_name_to_enrollments')
    @patch('manage_sections.views.unique_enrollments_not_in_section_filter')
    def test_enrollments_rendered_on_success(self, mock_filter, badge_filter, SDK_CONTEXT, render, get_section, is_editable_section, get_enrollments):
        """
        Test that sorted enrollments list is passed on to the rendered template
        """
        mock_enrollment_1 = {'user': {'sortable_name': 'e'}}
        mock_enrollment_2 = {'user': {'sortable_name': 'f'}}
        mock_enrollment_3 = {'user': {'sortable_name': 'g'}}
        badge_filter.return_value = [
            mock_enrollment_2, mock_enrollment_3, mock_enrollment_1
        ]
        sorted_enrollments = [
            mock_enrollment_1, mock_enrollment_2, mock_enrollment_3
        ]
        section_class_list(self.request, self.section_id)
        render.assert_called_with(
            self.request,
            'manage_sections/_section_classlist.html',
            {'enrollments': sorted_enrollments, 'allow_edit': ANY, 'section_id': ANY}
        )
